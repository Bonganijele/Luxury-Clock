# Copyright (c) 2024, Bongani. All rights reserved.
# This file is part of the  Luxury Digital Clock  project.


# Author: Bongani Jele <jelebongani43@gmail.com>

from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCore import Qt, QTimer, QTime, QSettings, QPoint, QRect


class PyToggle(QCheckBox):
    def __init__(self, bg_color="#000", circle_color="grey", active_color="#00BCff"):
        super().__init__()

        self.setCheckable(True)  
        self.setChecked(False)  

      

        self.setFixedSize(40, 20)
        self.setCursor(Qt.PointingHandCursor)

        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        # Load the saved state from QSettings
        self.settings = QSettings("BonganiTechnologies", "LuxuryClock")
        saved_state = self.settings.value("pytoggle_state", False, type=bool)
        self.setChecked(saved_state)  # Set the initial state to the saved value

        # Connect state change signal
        self.stateChanged.connect(self.on_state_changed)

    def is_checked(self):
        return self.isChecked()

    def on_state_changed(self):
        print(f"Status: {self.isChecked()}")
        # Save the current state to QSettings
        self.settings.setValue("pytoggle_state", self.isChecked())

    def hitButton(self, pos: QPoint):
        # Check if the click is within the toggle button's rectangle
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        # Set painter
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Set no pen for drawing
        p.setPen(Qt.NoPen)

        # Define the rectangle for drawing
        rect = QRect(0, 0, self.width(), self.height())

        # Background color
        if self.isChecked():
            p.setBrush(QColor(self._active_color))
        else:
            p.setBrush(QColor(self._bg_color))

        # Draw the rounded rectangle for the toggle background
        p.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

        # Draw the circle (toggle knob)
        circle_x = rect.width() - self.height() if self.isChecked() else 0
        p.setBrush(QColor(self._circle_color))
        p.drawEllipse(circle_x, 0, self.height(), self.height())

        p.end()
