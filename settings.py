from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QGroupBox, QMessageBox,
    QFileDialog, QComboBox, QDialog, QDialog, QTimeEdit, QDialogButtonBox,
    QListWidget, QSpacerItem, QSizePolicy, QCheckBox
    
)
from playsound import playsound  # Import playsound to play audio files
from PySide6.QtGui import QFont
import sys

class SettingWindow(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Settings")
        self.resize(400, 400)
        
