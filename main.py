import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
from threading import Thread
import random


class VerificationScreen(Screen):
    def __init__(self, **kwargs):
        super(VerificationScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.question, self.answer = self.generate_question()

        self.question_label = Label(text=f"Solve this: {self.question}")
        self.layout.add_widget(self.question_label)

        self.answer_input = TextInput(multiline=False)
        self.layout.add_widget(self.answer_input)

        self.verify_button = Button(text="Verify")
        self.verify_button.bind(on_press=self.verify_answer)
        self.layout.add_widget(self.verify_button)

        self.add_widget(self.layout)

    def generate_question(self):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        return f"{num1} + {num2}", str(num1 + num2)

    def verify_answer(self, instance):
        if self.answer_input.text == self.answer:
            self.manager.current = 'translator'
        else:
            self.answer_input.text = ''
            self.question, self.answer = self.generate_question()
            self.question_label.text = f"Solve this: {self.question}"


class TranslatorScreen(Screen):
    def __init__(self, **kwargs):
        super(TranslatorScreen, self).__init__(**kwargs)
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_label = Label(text="Enter text to translate or use voice command:")
        self.layout.add_widget(self.input_label)

        self.input_text = TextInput(multiline=True, height=100, size_hint_y=None)
        self.layout.add_widget(self.input_text)

        self.translate_button = Button(text="Translate")
        self.translate_button.bind(on_press=self.translate_text)
        self.layout.add_widget(self.translate_button)

        self.voice_button = Button(text="Speak")
        self.voice_button.bind(on_press=self.recognize_speech)
        self.layout.add_widget(self.voice_button)

        self.output_label = Label(text="Translated text:")
        self.layout.add_widget(self.output_label)

        self.output_text = TextInput(multiline=True, height=100, size_hint_y=None, readonly=True)
        self.layout.add_widget(self.output_text)

        self.speak_button = Button(text="Read Aloud")
        self.speak_button.bind(on_press=self.speak_text)
        self.layout.add_widget(self.speak_button)

        self.add_widget(self.layout)

    def translate_text(self, instance):
        def translate():
            input_text = self.input_text.text
            if input_text.strip():
                try:
                    translated = self.translator.translate(input_text, src='auto', dest='en')
                    self.update_output_text(translated.text)
                except Exception as e:
                    self.update_output_text(f"Error: {str(e)}")
            else:
                self.update_output_text("Please enter text to translate.")

        Thread(target=translate).start()

    def update_output_text(self, text):
        Clock.schedule_once(lambda dt: self.output_text.setter('text')(self.output_text, text))

    def recognize_speech(self, instance):
        def recognize():
            try:
                with sr.Microphone() as source:
                    self.update_output_text("Listening...")
                    audio = self.recognizer.listen(source)
                    try:
                        recognized_text = self.recognizer.recognize_google(audio)
                        self.update_input_text(recognized_text)
                        self.update_output_text("Recognized text: " + recognized_text)
                    except sr.UnknownValueError:
                        self.update_output_text("Could not understand the audio.")
                    except sr.RequestError as e:
                        self.update_output_text(f"Could not request results; {e}")
            except Exception as e:
                self.update_output_text(f"Error accessing microphone: {str(e)}")

        Thread(target=recognize).start()

    def update_input_text(self, text):
        Clock.schedule_once(lambda dt: self.input_text.setter('text')(self.input_text, text))

    def speak_text(self, instance):
        def speak():
            text = self.output_text.text
            if text.strip():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    self.update_output_text(f"Error: {str(e)}")
            else:
                self.update_output_text("No text to read aloud.")

        Thread(target=speak).start()


class TranslatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(VerificationScreen(name='verification'))
        sm.add_widget(TranslatorScreen(name='translator'))
        return sm


if __name__ == '__main__':
    TranslatorApp().run()
