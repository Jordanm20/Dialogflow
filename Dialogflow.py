import speech_recognition as sr
import pyttsx3
import os
import time
from google.cloud import dialogflow_v2beta1 as dialogflow

# Configuración de reconocimiento de voz
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Configuración de síntesis de voz
engine = pyttsx3.init('espeak')

# Configuración de Dialogflow
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './key.json'
project_id = 'dialogflow-388402'
session_id = 'Jordan'
language_code = 'es'

# Función para enviar una solicitud a Dialogflow y recibir una respuesta
def detect_intent_with_text_input(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session_path, query_input=query_input)

    return response.query_result.fulfillment_text

# Función para convertir texto a voz y reproducirlo en los parlantes
def speak(text):
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)  # Agregar un retraso de 1 segundo

# Bucle principal
while True:
    with microphone as source:
        print("Escuchando...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Procesando...")

    try:
        text_input = recognizer.recognize_google(audio, language='es')
        print("Input:", text_input)
        response = detect_intent_with_text_input(project_id, session_id, text_input, language_code)
        print("Output:", response)
        speak(response)
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError as e:
        print("Error al realizar la solicitud al servicio de reconocimiento de voz: {0}".format(e))
