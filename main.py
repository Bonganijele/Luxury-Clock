# Copyright (c) 2024, Bongani. All rights reserved.
# This file is part of the Luxury Digital Clock project.


# Author: Bongani Jele <jelebongani43@gmail.com>
from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QGroupBox, QMessageBox,
    QFileDialog, QComboBox, QDialog, QDialog, QTimeEdit, QDialogButtonBox,
    QListWidget, QSpacerItem, QSizePolicy, QCheckBox, QColorDialog, QSlider,QLineEdit, QInputDialog
    
)
from playsound import playsound
from PySide6.QtGui import QFont, QIcon
import threading
from settings import SettingWindow

from PySide6.QtGui import QFont, QColor, QPainter, QPixmap,  QMovie , QBrush,  QRegion, QBitmap

from PySide6.QtCore import Qt, QTimer, QTime, QSettings, QPoint, QRect, QThread, Signal, QDate
from pynput.keyboard import Key,Controller

from toggle_btn import PyToggle
from ai_logic import DigitalClockAI
from voice_thread import VoiceRecognitionThread

import threading
import pyttsx3
import sys
import os
import webbrowser
import simpleaudio as sa
import requests
import json
from datetime import datetime
import locale
import time
import subprocess
from pydub import AudioSegment
from pydub.playback import play





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.alarm_time = None  # Initialize alarm time as None
        self.selected_song = None  # Selected song path
       
        

        # Event to signal the thread to stop
        self.stop_event = threading.Event()
        self.play_thread = None 
    
        self.keyboard = Controller()
        self.previous_volume = 0

        # Initialize the slider value tracking
        self.previous_slider_value = 0
        self.ai = DigitalClockAI()

    def init_ui(self):
        
        self.setWindowTitle("Luxury Clock")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.resize(800, 500)
        
        
        self.settings = QSettings("YourCompany", "YourApp")
        self.is_listening = False
        self.listener_thread = None
        
        # Mute AI Volume (Voice)
        self.is_muted = False
        

      
        
       # Load the saved API key (if any) when the application starts
        self.load_api_key()
        
      
        
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        
        self.show_seconds = False  # By default, seconds are not shown
        self.time_format_24hr = False
        
        
         # Initialize alarm time and chosen song
        self.alarm_time = None
        self.chosen_song = None
        
        self.time_elapsed = 0

        # Set font size for the time display
        font = QFont()
        font.setPointSize(96)
        
        
        date_label_font = QFont()
        date_label_font.setPointSize(16)
        
        self.stopwatch_running = False
        
        # Set font for the AM/PM display
        self.ampm_font = QFont()
        self.ampm_font.setPointSize(25)

        # Create a central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(5)  
        main_layout.setContentsMargins(0, 0, 0, 0)  

        # GroupBox for Time, Date, and Buttons
        self.groupbox = QGroupBox()
       
        self.groupbox.setMinimumSize(650, 200)  

        self.groupbox_layout = QVBoxLayout()
        self.groupbox_layout.setSpacing(2)
        self.groupbox_layout.setContentsMargins(5, 5, 5, 5)  
        
        self.stopwatch_label = QLabel("00:00:00", self)
        self.stopwatch_label.setVisible(False)
        self.stopwatch_label.setFont(font)
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.stopwatch_label)


        self.time_date = QLabel(self)
        self.time_date.setFont(font)
        self.time_date.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.time_date)
        
        self.ampm_label = QLabel(self)
        self.ampm_label.setFont(self.ampm_font)
        self.ampm_label.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.ampm_label)

        
        self.temp_layout = QHBoxLayout()

        # Label to display weather output
        self.weather_output = QLabel(self)
        self.weather_output.setFixedHeight(50)
        self.weather_output.setWordWrap(True)
        self.weather_output.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.weather_output)

        
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.status_label)
        

    
        
        self.Humidity  = QLabel("Humidity: N/A", self)
        self.Humidity.setContentsMargins(10, 15, 0, 0)
        self.Humidity.setAlignment(Qt.AlignCenter)
        self.temp_layout.addWidget(self.Humidity)
        
        self.weather_Description = QLabel("Weather description: N/A")
        self.weather_Description.setContentsMargins(10, 15, 0, 0)
        self.weather_Description.setAlignment(Qt.AlignCenter)
        self.temp_layout.addWidget(self.weather_Description)
        
                
        self.min_temp = QLabel("Temp: N/A", self) 
        self.min_temp.setContentsMargins(0, 15, 0, 0)
        self.min_temp.setAlignment(Qt.AlignCenter)
        self.temp_layout.addWidget(self.min_temp)
        
        
        self.display_weather = QLabel("Weather Info for: N/A", self)
        self.display_weather.setAlignment(Qt.AlignCenter)
        self.display_weather.setVisible(False)
            
        
        self.groupbox_layout.addLayout(self.temp_layout)
        
        
        # Date and Month label, close to the time label
        self.date_label = QLabel(self)
        self.date_label.setFont(date_label_font)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.groupbox_layout.addWidget(self.date_label)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)  
        button_layout.setContentsMargins(0, 20, 0, 0) 

        
        # Alarm button
        self.alarm_button = QPushButton("Alarm")
        self.alarm_button.setFixedSize(100, 30)
        self.alarm_button.setStyleSheet("margin: 0px; padding: 0px;")
        self.alarm_button.clicked.connect(self.show_alarm_dialog)  
        button_layout.addWidget(self.alarm_button)


        self.start_stop_button = QPushButton("Start", self)
        self.start_stop_button.setFixedSize(100, 30)
        self.start_stop_button.clicked.connect(self.toggle_stopwatch)
        self.start_stop_button.setStyleSheet("margin: 0px; padding: 0px;")
        button_layout.addWidget(self.start_stop_button)
        
        
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setFixedSize(100, 30)
        self.reset_button.clicked.connect(self.reset_stopwatch)
        self.reset_button.setStyleSheet("margin: 0px; padding: 0px;")
        button_layout.addWidget(self.reset_button)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedSize(100, 30)
        self.settings_button.setStyleSheet("margin: 0px; padding: 0px;")
        self.settings_button.clicked.connect(self.show_settings_dialog)  
        button_layout.addWidget(self.settings_button)
        
        
        self.groupbox_layout.addLayout(button_layout)

        self.groupbox.setLayout(self.groupbox_layout)
        main_layout.addWidget(self.groupbox, alignment=Qt.AlignCenter)  # Center the group box in the main layout

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.timeout.connect(self.check_alarm)
        self.timer.start(1000)  # Update every second

        # Initialize time and date display
        self.update_time()

      
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stopwatch) 
        self.timer.setInterval(100)  

        # Initialize the stopwatch time
        self.stopwatch_time_elapsed = 0
        
        self.update_time()

         # Initialize time format from settings
        self.load_time_format()
        

    
        
    
    def toggle_stopwatch(self):
        """Toggle the stopwatch between start and stop."""
        if not self.stopwatch_running:
            # Start the stopwatch
            self.timer.start()
            self.stopwatch_running = True
            self.start_stop_button.setText("Stop")
            
            
            self.time_date.hide()
            self.ampm_label.hide()
            self.date_label.hide() 
            self.status_label.hide()
            self.min_temp.hide()
            self.weather_Description.hide()
            self.Humidity.hide()
            self.stopwatch_label.setVisible(True)  
        else:
            # Stop the stopwatch
            self.timer.stop()
            self.stopwatch_running = False
            self.start_stop_button.setText("Start")
            self.time_date.show()  
            self.ampm_label.show()
            self.date_label.show()
            self.status_label.show()
            self.min_temp.show()
            self.weather_Description.show()
            self.Humidity.show()
        
            self.stopwatch_label.setVisible(False)

    

    def reset_stopwatch(self):
        """Reset the stopwatch to zero and reset the display."""
        self.stopwatch_time_elapsed = 0
        self.update_stopwatch_display()
        
        
  
    def update_stopwatch(self):
        """Update the stopwatch time."""
        self.stopwatch_time_elapsed += 1 
        self.update_stopwatch_display()  

      
    def update_stopwatch_display(self):
        """Update the stopwatch label to show the elapsed time."""
        total_seconds = self.stopwatch_time_elapsed / 10
        hours, remainder = divmod(self.stopwatch_time_elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.stopwatch_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
  

   
    def update_time(self):
        """Update the time and date labels based on the selected format."""
        now = datetime.now()

        if self.time_format_24hr:
            # 24-hour format: No AM/PM
            formatted_time = now.strftime("%H:%M")  # 24-hour format
            self.ampm_label.setText("")

           
        else:
            # 12-hour format with AM/PM
            formatted_time = now.strftime("%I:%M")  # 12-hour format without AM/PM
            formatted_ampm = now.strftime("%p")  # AM/PM (AM or PM)
            self.ampm_label.setText(formatted_ampm)  # Set the AM/PM label

        # Optionally add seconds to the time display
        if self.show_seconds:
            formatted_time += now.strftime(":%S")

        self.time_date.setText(formatted_time)
        self.date_label.setText(now.strftime("%A, %d %b"))
        
    
    def process_command(self, command):
        print(f"[DEBUG] Handling command: {command}")
        if 'time' in command:
            current_time = datetime.now().strftime("%I:%M %p")
            print(f"[DEBUG] Current time: {current_time}")
            self.ai.speak(f"The current time is {current_time}")
        elif 'weather' in command:
            
            self.ai.speak("Which city's weather would you like to know?")
            city = self.ai.listen()
            if city:
                weather_info = self.ai.get_weather(city)
                self.ai.speak(weather_info)
        elif 'joke' in command:
            
            joke = self.ai.tell_joke()
            print(f"[DEBUG] Telling joke: {joke}")
            self.ai.speak(joke)
        elif 'hello' in command or 'hi' in command:
            response = self.ai.handle_custom_greetings(command)
            print(f"[DEBUG] Greeting response: {response}")
            self.ai.speak(response or "Hello! How can I assist you today?")
            
        elif any(keyword in command for keyword in ["ask", "question", "inquire", "please can I ask you something"]):
            self.ai.speak("What would you like to ask?")
            user_query = self.ai.listen()
            if user_query:
                print(f"User query received: {user_query}")
                response = self.ai.get_openai_response(user_query)
                print(f"OpenAI response: {response}")
                self.ai.speak(response)
        
        elif 'exit' in command or 'quit' in command or 'stop' in command:
            self.ai.speak("Goodbye!")
            self.voice_thread.terminate()  # Properly terminate the voice thread
            self.close()  # Close the window
        else:
            self.ai.speak("I'm sorry, I didn't understand that command.")
            print("[DEBUG] Command not recognized.")

    
    
    def toggle_time_format(self):
        """Toggle between 12-hour and 24-hour format when the button is clicked."""
        self.time_format_24hr = not self.time_format_24hr
        
        
        settings = QSettings("Bonganitechnologies", "LuxuryClock")
        settings.setValue("time_format_24hr", self.time_format_24hr)
        if self.time_format_24hr:
            self.change_format.setText("12-hour format")
        else:
            self.change_format.setText("24-hour format")
        
        # Update the displayed time
        self.update_time()

    def load_time_format(self):
        """Load the saved time format from QSettings."""
        settings = QSettings("Bonganitechnologies", "LuxuryClock")
        self.time_format_24hr = settings.value("time_format_24hr", True, type=bool)
    
    
   
        
       
    
    
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        
        # self.previous_slider_value = 0  # Initialize this in the constructor
        self.settings = QSettings("LuxuryClock", "SliderApp")
        
        setting_dialog = QDialog(self)
        setting_dialog.setWindowTitle("Settings")
        setting_dialog.setFixedSize(440, 430)

        # Create a vertical layout for the settings dialog
        setting_layout = QVBoxLayout()

        lb = QLabel("Change Theme:")
        setting_layout.addWidget(lb)

        button_layout = QHBoxLayout()
        
        self.button = QPushButton("Choose Colors")
        button_layout.addWidget(self.button)
        
     
        
        self.button1 = QPushButton("Default")
        self.button1.clicked.connect(self.reset_to_default_col)
        button_layout.addWidget(self.button1)
        setting_layout.addLayout(button_layout)
        
        lb1 = QLabel("Font Size:")
        setting_layout.addWidget(lb1)
        
        slide_btn_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(8, 25)
        self.slider.setValue(1)
        self.slider.setToolTip('Increase or Decrease Font Size.')
        self.slider.setMaximumWidth(170)
        self.slider.valueChanged.connect(self.update_ampm_size)
        setting_layout.addWidget(self.slider)
        
        saved_value = self.settings.value("sliderValue", 50, type=int)
        self.slider.setValue(saved_value)
        
        self.previous_slider_value = self.slider.value()  # Initialize previous value
        
        self.slider.valueChanged.connect(self.update_ampm_size)
        self.slider.valueChanged.connect(self.save_slider_value)
        
       
        
        
        self.button3 = QPushButton("Reset to default")
        self.button3.clicked.connect(self.default_size)
        slide_btn_layout.addWidget(self.button3)

        setting_layout.addLayout(slide_btn_layout)
        
        
        self.time_format = QLabel("Time Format:")
        setting_layout.addWidget(self.time_format)
        
        
        time_layout_format = QHBoxLayout()
        
        
       
        
        self.add_secs = PyToggle()
        self.add_secs.setToolTip("Enable seconds display on clock")
        self.add_secs.clicked.connect(self.toggle_seconds)
        self.add_secs.clicked.connect(self.save_toggle_state)
        self.add_secs.setChecked(self.show_seconds)  # Set toggle to saved state
        
        
        self.load_toggle_state()

        time_layout_format.addWidget(self.add_secs)
      
        self.change_format = QPushButton("24 hour format", self)
        self.change_format.clicked.connect(self.toggle_time_format)
        self.change_format.setFixedWidth(120)
        time_layout_format.addWidget(self.change_format)
        
        

        setting_layout.addLayout(time_layout_format)
        
        self.weather_label = QLabel("Weather Service:")
        setting_layout.addWidget(self.weather_label)
        
         # Weather input field
         
        # Create a vertical layout for the weather input and API key
        weather_layout = QVBoxLayout()

        # Create the weather input
        self.weather_input = QLineEdit(self)

        self.weather_input.setPlaceholderText("Enter city name")
        self.weather_input.returnPressed.connect(self.save_weather_data)
        self.weather_input.setContentsMargins(12, 0, 0, 0)
        self.weather_input.setMaxLength(16)
        weather_layout.addWidget(self.weather_input)

       

        weather_btn_layout = QHBoxLayout()

        # Create the save button
        self.btn = QPushButton("Save", self)
        self.btn.setFixedHeight(26)
        self.btn.setFixedWidth(120)
        self.btn.setContentsMargins(12, 0, 0, 0)
        self.btn.clicked.connect(self.save_weather_data)
        weather_btn_layout.addWidget(self.btn)
        
        
        self.get_api_key_btn = QPushButton("Get API Key")
        self.get_api_key_btn.setFixedHeight(26)
        self.get_api_key_btn.setToolTip("Go get your api key from openweather website")
        self.get_api_key_btn.setFixedWidth(120)
        self.get_api_key_btn.clicked.connect(self.recieve_api)
        weather_btn_layout.addWidget(self.get_api_key_btn)

        weather_layout.addLayout(weather_btn_layout)

        # Add the weather layout to the parent layout
        setting_layout.addLayout(weather_layout)

        
        
        self.ai_assistant = QLabel("Ai Assistant Management:")
        setting_layout.addWidget(self.ai_assistant)
        
        
        
        self.current_vol =  self.get_current_volume()
        self.vol_label = QLabel(f"Vol: {self.current_vol}%")
        setting_layout.addWidget(self.vol_label)
        
        self.ai_vol_silder = QSlider(Qt.Horizontal)
        self.ai_vol_silder.setRange(0, 100)
        self.ai_vol_silder.setValue(self.current_vol)
        setting_layout.addWidget(self.ai_vol_silder)
        
        self.ai_vol_silder.valueChanged.connect(self.update_volume)
        
        
         
        open_ai_layout = QHBoxLayout()
        
        self.open_ai_input = QLineEdit(self)
        self.open_ai_input.setPlaceholderText("Enter OpenAI API Key")
        self.open_ai_input.setContentsMargins(12, 0, 0, 0)
        open_ai_layout.addWidget(self.open_ai_input)
        
        self.save_openai_key_btn = QPushButton("Save Key")
        self.save_openai_key_btn.setFixedWidth(100)
        open_ai_layout.addWidget(self.save_openai_key_btn)
        
        
        setting_layout.addLayout(open_ai_layout)
       

        ai_layout = QHBoxLayout()
        
        self.toggle_listen_button = QPushButton("Start Listening", self)
        self.toggle_listen_button.setToolTip("Enable AI Assistant ")
        self.toggle_listen_button.clicked.connect(self.toggle_listening)
        self.toggle_listen_button.move(50, 50)
        ai_layout.addWidget(self.toggle_listen_button)
        
        
        self.voice_thread = VoiceRecognitionThread(self.ai)
        
        self.ai_mute_btn = QPushButton("Mute", self)
        self.ai_mute_btn.setFixedWidth(100)
        self.ai_mute_btn.clicked.connect(self.mute_ai_assistant)
        ai_layout.addWidget(self.ai_mute_btn)
        
        
        setting_layout.addLayout(ai_layout)
       
        
        
    
        self.listening = False 

        # Automatically initialize city data on startup
        # And I dont know why it doesnt automatically load the city name 
        # without opening settings window
        self.initialize()
    
         # Update the time display based on the loaded state
        self.update_time()

        def choose_color():
            color = QColorDialog.getColor()  
            if color.isValid():  
                self.setStyleSheet(f"background-color: {color.name()};")
                
                
               # When opening the settings dialog, restore the saved colors for each button:
            for i, btn in enumerate([self.settings_button, self.button1, self.button3,
                                     self.button, self.alarm_button,]):
                saved_color = self.settings.value(f"button{i}_color", "#26262A")  # Default to black if no color is saved
                btn.setStyleSheet(f"background-color: {saved_color}; color: white;")

        for i, btn in enumerate([self.settings_button, self.button1, self.button3,
                                 self.button,  self.alarm_button, self.btn, self.ai_mute_btn,
                                 self.change_format, self.start_stop_button, self.reset_button,
                                 self.get_api_key_btn, self.toggle_listen_button, self.save_openai_key_btn
                                
                                 ]):
            saved_color = self.settings.value(f"button{i}_color", "#26262A")  # Default to black if no color is saved
            btn.setStyleSheet(f"background-color: {saved_color}; color: white;")          

            # Connect the button click to the color picker function
        self.button.clicked.connect(choose_color)
            
        setting_dialog.setLayout(setting_layout)
        setting_dialog.exec()
    
    def toggle_seconds(self):
            """Toggle the display of seconds when the button is clicked."""
            self.show_seconds = not self.show_seconds
            print(f"Seconds enabled: {self.add_secs.isChecked()}")
            self.settings.setValue("show_seconds", self.add_secs.isChecked())
            self.update_time()
     
    
    def save_toggle_state(self):
        """Save the toggle state to QSettings."""
        self.settings.setValue("show_seconds", self.add_secs.isChecked())

    def load_toggle_state(self):
        """Load the toggle state from QSettings."""
        saved_state = self.settings.value("show_seconds", False, type=bool)
        self.add_secs.setChecked(saved_state)
        self.show_seconds = saved_state

    
    
    def save_weather_data(self):
        """Fetch weather data, save city name, and display it when the 'Save' button is clicked."""
        city_name = self.weather_input.text()
        if city_name:
            # Use QSettings to save the city name
            settings = QSettings("Bonganitechnologies", "LuxuryClock")
            settings.setValue("saved_city", city_name)

            # Fetch weather data and display it
            weather_info = self.get_weather_data(city_name)
            self.display_weather.setText(f"Weather Info for {city_name}: {weather_info}")
        else:
            self.display_weather.setText("Please enter a city name.")

    def load_saved_city(self):
        """Load the saved city name using QSettings."""
        settings = QSettings("Bonganitechnologies", "LuxuryClock")  
        saved_city = settings.value("saved_city", "")  # Default to an empty string if no city saved

        if saved_city:
            self.weather_input.setText(saved_city)
            self.save_weather_data()  # Automatically fetch and display weather info
        else:
            self.weather_input.setText("")  # Clear input if no city is found

    def initialize(self):
        """Initialize the weather input with the saved city and automatically click the button."""
        self.load_saved_city()

         # Load the saved state from QSettings
        self.load_listening_state()
        
    def load_listening_state(self):
        """Load the saved state from QSettings."""
        # Check if the 'is_listening' state was saved
        saved_state = self.settings.value("is_listening", False, bool)
        if saved_state:
            # If the state is True, start listening mode
            self.is_listening = True
            self.toggle_listen_button.setText("Stop Listening")
            self.status_label.setText("Listening...")

    def save_listening_state(self):
        """Save the current listening state to QSettings."""
        self.settings.setValue("is_listening", self.is_listening)

    def toggle_listening(self):
        if not self.is_listening:
            print("[DEBUG] Starting to listen continuously...")
            self.is_listening = True
            self.toggle_listen_button.setText("Stop Listening")
            
            # Display the GIF to indicate listening state
            self.status_label.setText("Listening...")

            self.listener_thread = VoiceRecognitionThread(self.ai)
            self.listener_thread.command_received.connect(self.process_command)
            self.listener_thread.start()

        else:
            print("[DEBUG] Stopping continuous listening...")
            self.is_listening = False
            self.toggle_listen_button.setText("Start Listening")
            
            # Stop the GIF when not listening
            self.status_label.clear()  # Clear the label (stop the GIF)

            self.listener_thread.terminate()

        # Save the state after toggling
        self.save_listening_state()
    
    
    
    def get_weather_data(self, city_name):
        """Fetch weather data for the city entered in the QLineEdit."""
        city_name = self.weather_input.text()

        if not city_name:
            self.weather_output.setText("Please enter a city name.")
            return

        try:
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = f"{base_url}appid={self.api_key}&q={city_name}"

            response = requests.get(complete_url)

            if response.status_code == 200:
                data = response.json()

                if data["cod"] != "404":
                    y = data["main"]
                    self.current_temperature = y["temp"] - 273.15  # Convert from Kelvin to Celsius
                    self.current_humidity = y["humidity"]
                    self.weather_description = data["weather"][0]["description"]

                

                    
                    self.min_temp.setText(f"Temp: {self.current_temperature:.2f}°C")
                    self.Humidity.setText(f"Humidity: {self.current_humidity}%")
                    self.weather_Description.setText(f"Weather description:   {self.weather_description}")

                else:
                    self.weather_output.setText("City not found.")
            else:
                self.weather_output.setText("Failed to retrieve weather data.")
        except requests.exceptions.RequestException as e:
            self.weather_output.setText(f"Error: {e}")


    def recieve_api(self):
        
        weather_key_input, ok = QInputDialog().getText(self, "Enter API Key", "Please enter your weather API key:")
        
        if ok and weather_key_input:
            self.api_key = weather_key_input
            
            settings = QSettings("BonganiTechnologies", "LuxuryClock")
            settings.setValue("weather_api_key",  self.api_key)
            
            QMessageBox.information(self, "API Key received:", self.api_key)
            # print("API Key received:", self.api_key)
        else:
            QMessageBox.warning(self, "Error", "API Key input was canceled or empty.")
            # print("API Key input was canceled or empty.")
              
    def load_api_key(self):
        
        settings = QSettings("BonganiTechnologies", "LuxuryClock")
        self.api_key = settings.value("weather_api_key", "")
        if self.api_key:
            print("Loaded API Key:", self.api_key)  # For debugging or verification
        else:
            print("No API Key found.")
  
    def reset_to_default_col(self):
        default_col = QColor("#252525")
        if default_col.isValid():
            self.setStyleSheet(f"background-color: {default_col.name()};")

        self.keyboard = Controller()
        
        
    def get_current_volume(self):
        """Retrieve the current system volume level (0-100)."""
        try:
            output = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]).decode('utf-8')
            volume = output.split('/')[1].strip().replace('%', '')
            return int(volume)
        except Exception as e:
            print(f"Error getting volume: {e}")
            QMessageBox.warning("Error", f"Error getting volume: {e}")
            return 50  # Default to 50 if there's an error

    def set_volume(self, volume_level):
        """Set the system volume to the given level."""
        try:
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume_level}%"])
        except Exception as e:
            print(f"Error setting volume: {e}")

    def update_volume(self, value):
        """Update the volume label and system volume when the slider value changes."""
        self.vol_label.setText(f"Vol: {value}%")
        self.set_volume(value)

         
    def mute_ai_assistant(self):
        if not self.is_muted:
            # Mute the assistant
            self.keyboard.press(Key.media_volume_mute)
            self.keyboard.release(Key.media_volume_mute)
            self.ai_mute_btn.setText("Unmute")  # Change button text to "Unmute"
            self.is_muted = True
        else:
            # Unmute the assistant
            self.keyboard.press(Key.media_volume_mute)
            self.keyboard.release(Key.media_volume_mute)
            self.ai_mute_btn.setText("Mute")  # Change button text back to "Mute"
            self.is_muted = False
             
    def show_alarm_dialog(self):

        """Show the alarm dialog with options to select a song, set a time, and repeat days."""

        alarm_dialog = QDialog(self)
        alarm_dialog.setWindowTitle("Set Alarm Time")
        alarm_dialog.setFixedSize(400, 400)
        alarm_dialog.setStyleSheet("""

            QDialog { 
                border-radius: 15px; 
                padding: 20px;

            }

            QLabel { 
                font-size: 16px;
                font-weight: bold; 
                color: #333; 

            }

            QTimeEdit {
                font-size: 24px;
                border: 2px solid #00796b;
                border-radius: 5px;
                padding: 5px;

            }

        """)
        layout = QVBoxLayout(alarm_dialog)

        # Time selection
        time_group = QGroupBox("Set Alarm Time")
        time_layout = QHBoxLayout()

        

        self.hours_edit = QTimeEdit()
        self.hours_edit.setDisplayFormat("HH:mm")  # 24-hour format
        self.hours_edit.setFont(QFont('Arial', 24))
        self.hours_edit.setStyleSheet("background-color: #26262A; ")
        self.hours_edit.setTime(QTime.currentTime())
        
        time_layout.addWidget(self.hours_edit)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)


        # Song selection
        song_group = QGroupBox("Select Alarm Song")
        song_layout = QHBoxLayout()

        

        self.choose_button = QPushButton("Choose Device Sounds")
        self.choose_button.setFixedHeight(30)
        self.choose_button.clicked.connect(self.choose_song)  # Placeholder for song selection
        self.choose_button.setStyleSheet("background-color: #26262A; ")
        song_layout.addWidget(self.choose_button)
        song_group.setLayout(song_layout)
        layout.addWidget(song_group)


        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("background-color: #26262A; ")
        button_box.accepted.connect(lambda: self.set_alarm(alarm_dialog))
        button_box.rejected.connect(alarm_dialog.reject)
        layout.addWidget(button_box)


        alarm_dialog.setLayout(layout)
        alarm_dialog.show()

   

    

    def set_alarm(self, alarm_dialog: QDialog):
        """Set the alarm time from the QTimeEdit widget."""
        self.alarm_time = self.hours_edit.time()  # Get the selected time from QTimeEdit
        if self.alarm_time.isValid():
            print(f"Alarm set for {self.alarm_time.toString()}")
            self.timer.start(1000)  # Check every second
            alarm_dialog.accept()  # Close the dialog if the time is set successfully
        else:
            print("Invalid time selected.")

    def choose_song(self):
        """Open a file dialog to choose a song for the alarm."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose Alarm Sound", "", 
                                                    "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)", 
                                                    options=options)
        if file_name:
            # Store the selected song path
            self.selected_song = file_name
            song_name = os.path.basename(file_name)
            QMessageBox.information(self, "Song Selected", f"You have selected: {song_name}")
        else:
            QMessageBox.warning(self, "No Selection", "No song was selected.")

    def check_alarm(self):
        """Check if the current time matches the alarm time."""
        if self.alarm_time:  # Ensure an alarm time is set
            current_time = QTime.currentTime()
            if current_time >= self.alarm_time:
                self.trigger_alarm()
                self.alarm_time = None  # Reset after the alarm goes

  
   
    def trigger_alarm(self):
        """Play the selected alarm song in a loop until 'OK' is clicked or 4 minutes pass."""
        if self.selected_song:
            self.stop_event.clear()  # Clear the stop event for a new alarm
            self.play_thread = threading.Thread(target=self.play_song)
            self.play_thread.start()

            # Show dialog with "OK" button to stop the alarm
            result = QMessageBox.information(None, "Alarm Triggered", 
                                             "Time's up! The alarm is ringing!", 
                                             QMessageBox.Ok)
            if result == QMessageBox.Ok:
                self.stop_event.set()  # Signal the thread to stop
                self.stop_music()
        else:
            QMessageBox.warning(None, "No Song Selected", "Please select a song for the alarm.")

    def play_song(self):
        """Play the selected song, looping up to 4 minutes or until stop_event is set."""
        try:
            audio = AudioSegment.from_file(self.selected_song)
            play_time_limit = 2 * 60 * 1000  # 2 minutes in milliseconds
            start_time = QTime.currentTime()

            while not self.stop_event.is_set():
                # Check if 4 minutes have passed
                elapsed_time = start_time.msecsTo(QTime.currentTime())
                if elapsed_time >= play_time_limit:
                    break
                # Play the song
                play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, 
                                          bytes_per_sample=audio.sample_width, 
                                          sample_rate=audio.frame_rate)
                
                while play_obj.is_playing() and not self.stop_event.is_set():
                    pass  # Wait while the song plays

                # Stop playback if stop_event is set
                if self.stop_event.is_set():
                    play_obj.stop()
                    break
        except Exception as e:
            QMessageBox.critical(None, "Error Playing Song", f"An error occurred: {str(e)}")

    def stop_music(self):
        """Stop the currently playing music."""
        self.stop_event.set()  # Signal the thread to stop

    
    def update_ampm_size(self, new_value):
        """Update the size of the AM/PM label font based on slider value."""
        current_size = self.ampm_font.pointSize()

        # Initialize previous_slider_value if it doesn't exist yet
        if not hasattr(self, 'previous_slider_value'):
            self.previous_slider_value = new_value

        # Adjust font size based on slider movement
        if new_value > self.previous_slider_value:
            self.ampm_font.setPointSize(current_size + 2)
        elif new_value < self.previous_slider_value:
            new_size = max(current_size - 2, 1)  # Ensure font size doesn't go below 1
            self.ampm_font.setPointSize(new_size)

        self.ampm_label.setFont(self.ampm_font)
        self.previous_slider_value = new_value

    def default_size(self):
        """Set the default font size for the AM/PM label."""
        default_font = QFont()
        default_font.setPointSize(25)

        # Apply default font size to the ampm label
        self.ampm_font = default_font
        self.ampm_label.setFont(self.ampm_font)
            
    def save_slider_value(self, value):
        self.settings.setValue("sliderValue", value)
        
        
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
    
