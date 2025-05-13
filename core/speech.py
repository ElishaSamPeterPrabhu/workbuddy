"""
Speech recognition thread for WorkBuddy (Jarvis Assistant).

Handles background voice input (to be integrated after core text features).

TODO: Migrate this to /core/speech.py and integrate with PyQt6 UI in the future.
"""

import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal


class SpeechRecognitionThread(QThread):
    text_recognized = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.is_running = True

    def run(self):
        """Main method that runs on the separate thread"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen for speech
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Convert speech to text
                text = self.recognizer.recognize_google(audio)

                # Emit signal with recognized text
                self.text_recognized.emit(text)

        except sr.WaitTimeoutError:
            self.text_recognized.emit("")
        except sr.UnknownValueError:
            self.text_recognized.emit("")
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            self.text_recognized.emit("")
        except Exception as e:
            print(f"Speech recognition error: {e}")
            self.text_recognized.emit("")

    def stop(self):
        """Stop the speech recognition"""
        self.is_running = False
        self.terminate()  # This will terminate the thread
