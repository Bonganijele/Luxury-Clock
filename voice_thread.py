from PySide6.QtCore import QThread, Signal

class VoiceRecognitionThread(QThread):
    command_received = Signal(str)

    def __init__(self, ai):
        super().__init__()
        self.ai = ai

    def run(self):
        while True:
            command = self.ai.listen()
            if command:
                print(f"[DEBUG] Emitting command: {command}")
                self.command_received.emit(command)




