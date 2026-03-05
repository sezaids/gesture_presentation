import speech_recognition as sr
import threading

class VoiceController:
    def __init__(self):
        self.command = ""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.thread = threading.Thread(target=self._listen_continuous, daemon=True)
        self.thread.start()

    def _listen_continuous(self):
        while True:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit = 4)
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Voice Command: {text}")
                    self.command = text
                except:
                    pass

    def get_command(self):
        cmd = self.command
        self.command = ""
        return cmd
