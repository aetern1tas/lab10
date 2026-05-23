import json
import time
import os
import requests
import pyttsx3
import pyaudio
import vosk
import webbrowser
from PIL import Image
from io import BytesIO
import subprocess

class Speech:
    def __init__(self):
        self.rate = 140

    def text2voice(self, text):
        subprocess.call(['say', '-r', str(self.rate), text])


class Recognize:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_small')
        model = vosk.Model(model_path)
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']


class DogAssistant:
    def __init__(self):
        self.speech = Speech()
        self.current_image = None
        self.current_url = None
        self.api_url = 'https://dog.ceo/api/breeds/image/random'

    def get_dog_image(self):
        response = requests.get(self.api_url)
        data = response.json()
        
        if data['status'] == 'success':
            self.current_url = data['message']
            image_data = requests.get(self.current_url).content
            self.current_image = Image.open(BytesIO(image_data))
            
            self.current_image.show()
            
            self.speech.text2voice('Готово')
            return True
        
        return False

    def save_image(self):
        if self.current_image:
            self.current_image.save('dog_image.jpg')
            self.speech.text2voice('сохранено')
        else:
            self.speech.text2voice('сначала получите изображение')

    def get_breed(self):
        
        if self.current_url is None:
            self.speech.text2voice('сначала получите изображение')
            return
        
        parts = self.current_url.split('/')
        breed = parts[-2].replace('-', ' ')
        
        print('порода собачки:', breed)
        
        if not breed or breed == 'breeds':
            self.speech.text2voice('порода не указана в ссылке')
        else:
            self.speech.text2voice('порода собачки: ' + breed)

    def get_resolution(self):
        if self.current_image:
            width, height = self.current_image.size
            text = 'разрешение: ' + str(width) + ' на ' + str(height) + ' пикселей'
            self.speech.text2voice(text)
        else:
            self.speech.text2voice('Сначала получите изображение')

    def process_command(self, text):
        text = text.lower()
        
        if text == 'закрыть' or text == 'выход':
            self.speech.text2voice('До свидания')
            return False
        
        elif text == 'покажи собаку' or text == 'ещё':
            self.get_dog_image()
        
        elif text == 'сохранить':
            self.save_image()
        
        elif text == 'назвать породу' or text == 'порода':
            self.get_breed()
        
        elif text == 'разрешение' or text == 'размер':
            self.get_resolution()
        
        else:
            print('распознано:', text)
        
        return True

    def run(self):
        recognizer = Recognize()
        self.speech.text2voice('ассистент готов показывать собак')
        
        for text in recognizer.listen():
            if not self.process_command(text):
                break


if __name__ == '__main__':
    assistant = DogAssistant()
    assistant.run()