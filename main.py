from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cv2
import os

from voice_module import VoiceController

voice_input = VoiceController()

width, height = 1280, 720
folderPath = "Presentation"

cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)

pathImages = sorted(os.listdir(folderPath), key=len)

imgNumber = 0
hs, ws = int(120*1), int(213*1)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 15
annotations = [[]]
annotationNumber = 0
annotationStart = False
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorNames = ["Blue", "Green", "Red", "Yellow"]
drawColor = colors[2]

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    for i, col in enumerate(colors):
        x_start = (i + 1) * 200 
        cv2.rectangle(imgCurrent, (x_start, 1), (x_start + 200, 50), col, cv2.FILLED)
        cv2.putText(imgCurrent, colorNames[i], (x_start + 50, 35), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0,255,0),10)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        if lmList[8][1] < 100:
            if 200 < lmList[8][0] < 400:
                drawColor = colors[0]
            elif 400 < lmList[8][0] < 600:
                drawColor = colors[1]
            elif 600 < lmList[8][0] < 800:
                drawColor = colors[2]
            elif 800 < lmList[8][0] < 1000:
                drawColor = colors[3]
            
            selected_box_index = int(lmList[8][0] // 200)
            cv2.rectangle(imgCurrent, (selected_box_index * 200, 0), 
                        ((selected_box_index + 1) * 200, 50), (255, 255, 255), 5)

        xVal = int(np.interp(lmList[8][0], [100, width - 100], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        if cy <= gestureThreshold:
            annotationStart = False
            if fingers == [1,0,0,0,0]:
                annotationStart = False
                print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1

            if fingers == [0,0,0,0,1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1

        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, drawColor, cv2.FILLED)
            annotationStart = False
        
        
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([drawColor]) 
            
            cv2.circle(imgCurrent, indexFinger, 12, drawColor, cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        if fingers == [0,1,1,1,0]:
            if annotations: 
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True
    else:
        annotationStart = False

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range(len(annotations)):
        if len(annotations[i]) > 1:
            lineColor = annotations[i][0]
            for j in range(2, len(annotations[i])):
                cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], lineColor, 12)

    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    # Logic: Aik hi variable mein command store karein
    command = voice_input.get_command()
    
    if command: # Agar koi voice suni gayi hai
        print(f"Suni gayi command: {command}") # Debugging ke liye
        
        if "next" in command:
            if imgNumber < len(pathImages) - 1:
                imgNumber += 1
                annotations = [[]]
                annotationNumber = 0
                print("Voice: Moving to Next Slide")

        elif "back" in command or "previous" in command:
            if imgNumber > 0:
                imgNumber -= 1
                annotations = [[]]
                annotationNumber = 0
                print("Voice: Moving Back")

        elif "clear" in command:
            annotations = [[]]
            annotationNumber = 0
            print("Voice: Screen Cleared")

        # Colors change karne ki logic
        elif "blue" in command: drawColor = colors[0]
        elif "green" in command: drawColor = colors[1]
        elif "red" in command: drawColor = colors[2]
        elif "yellow" in command: drawColor = colors[3]