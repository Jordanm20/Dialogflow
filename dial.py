from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech
import os
import speech_recognition as sr
import pygame
import random
# Configuración de Dialogflow CX
project_id = 'dialogflow-388402'
location = 'global'
agent_id = '18228ee1-52a5-4449-aefc-4d6502d9547d'
session_id = str(random.randint(1000, 9999))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './key.json'
# Configurar las opciones del cliente
client_options = ClientOptions(api_endpoint='dialogflow.googleapis.com')
# Crear una instancia del cliente de sesiones
session_client = dialogflow.SessionsClient(client_options=client_options)
# Iniciar una sesión de conversación
session_path = session_client.session_path(project_id, location, agent_id, session_id)
# Configurar el reconocimiento de voz
r = sr.Recognizer()
mic = sr.Microphone()
# Configurar la síntesis de voz
tts_client = texttospeech.TextToSpeechClient()
# Configurar la reproducción de audio
pygame.mixer.init()
# Ajustar el umbral de energía manualmente (puedes experimentar con diferentes valores)
r.energy_threshold = 4000
# Función para detectar y manejar la entrada de voz
def handle_voice_input():
    with mic as source:
        print("Di algo...")
        audio = r.listen(source)
    try:
        user_input = r.recognize_google(audio, language='es')
        return user_input
    except sr.UnknownValueError:
        print("No se pudo reconocer el habla")
        return ""
    except sr.RequestError:
        print("Error al conectarse al servicio de reconocimiento de voz")
        return ""
# Función para sintetizar y reproducir la respuesta de audio
def speak_response(response_texts):
    for response_text in response_texts:
        print("Bot:", response_text)
        # Sintetizar la respuesta de texto a voz
        input_text = texttospeech.SynthesisInput(text=response_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-419", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        response = tts_client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        # Guardar el audio en un archivo temporal
        temp_file = "temp_audio.wav"
        with open(temp_file, "wb") as f:
            f.write(response.audio_content)

        # Cargar y reproducir el audio utilizando pygame
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Eliminar el archivo temporal
        os.remove(temp_file)
        # Verificar si el mensaje indica "Digite su cédula"
        if "Digite su numero de cédula" in response_text or "Numero de cédula del titular del servicio de internet" in response_text:
            # Solicitar la cédula por teclado
            cedula = input("Ingrese su número de cédula: ")

            # Enviar la cédula a Dialogflow
            query_input = dialogflow.QueryInput(
                text=dialogflow.TextInput(text=cedula),
                language_code="es-419"
            )
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )
            # Obtener la respuesta de Dialogflow
            response = session_client.detect_intent(request=request)

            # Extraer y mostrar la respuesta del agente
            response_texts = []
            if response.query_result.response_messages:
                for message in response.query_result.response_messages:
                    if message.text.text:
                        response_texts.append(message.text.text[0])

            # Reproducir la respuesta de audio
            speak_response(response_texts)
# Interactuar con el agente de Dialogflow CX
while True:
    user_input = handle_voice_input()
    # Si no se reconoce ninguna entrada de voz, continuar al siguiente ciclo
    if not user_input:
        continue
    # Crear una solicitud de detección de intención
    query_input = dialogflow.QueryInput(
        text=dialogflow.TextInput(text=user_input),
        language_code="es-419"
    )
    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=query_input
    )
    # Enviar la solicitud y recibir la respuesta
    response = session_client.detect_intent(request=request)
    # Extraer y mostrar la respuesta del agente
    response_texts = []
    if response.query_result.response_messages:
        for message in response.query_result.response_messages:
            if message.text.text:
                response_texts.append(message.text.text[0])
    speak_response(response_texts)