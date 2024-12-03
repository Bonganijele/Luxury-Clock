# In ai_logic.py
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import requests
import openai
from datetime import datetime

class DigitalClockAI:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.api_key = '' # PLEASE ENTER YOUR WEATHER API KEY

        self.greetings = ["hello anna", "hi anna"]
        self.greetings_responses = [
            "I am Anna, online and ready. How may I assist you today?",
            "I am online and ready!",
            "Always here for you!"
        ]
        
    def speak(self, text):
        print(f"[DEBUG] Speaking: {text}")
        try:
            tts = gTTS(text, lang="en")
            with io.BytesIO() as audio_file:
                tts.write_to_fp(audio_file)
                audio_file.seek(0)
                audio = AudioSegment.from_file(audio_file, format="mp3")
                play(audio)
        except Exception as e:
            print(f"[ERROR] Error during speech synthesis: {e}")

    def listen(self):
        try:
            print("[DEBUG] Adjusting for ambient noise...")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("[DEBUG] Listening for command...")
                audio = self.recognizer.listen(source)
                print("[DEBUG] Processing the audio...")
                query = self.recognizer.recognize_google(audio)
                print(f"[DEBUG] Command recognized: {query}")
                return query
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            self.speak("Sorry, my speech service is down.")
            return ""

    def get_weather(self, city):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"The weather in {city} is {weather} with a temperature of {temperature} degrees Celsius."
        else:
            return "Sorry, I couldn't fetch the weather information."

    def tell_joke(self):
        try:
            response = requests.get('https://v2.jokeapi.dev/joke/Any?type=single')
            joke_data = response.json()
            return joke_data.get('joke', "I'm sorry, I couldn't find a joke right now.")
        except Exception as e:
            return f"Could not retrieve a joke. Error: {str(e)}"

    def handle_custom_greetings(self, query):
        for greet, response in zip(self.greetings, self.greetings_responses):
            if greet in query:
                return response
        return None 

    def get_openai_response(self, user_query):
        try:
            response = self.client.chat.completions.create(
                prompt=user_query,
                model="gpt-4o-mini",
                messages=[{"role": "user",
                           "content": user_query}],
                max_tokens=330
            )
             # Assuming the response structure has a 'choices' field
            return response['choices'][0]['message']['content']
        except openai.APIError as e:
            print(f"OpenAI API returned an API Error: {e}")
            return "Sorry, I couldn't get a response from OpenAI."
        except openai.APIConnectionError as e:
            print(f"Failed to connect to OpenAI API: {e}")
            return "Sorry, there seems to be a connection issue."
        except openai.RateLimitError as e:
            print(f"OpenAI API request exceeded rate limit: {e}")
            return "I'm being rate-limited; please try again later."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Sorry, an unexpected error occurred."