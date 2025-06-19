import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import requests
import openai

# Configura la API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    response = VoiceResponse()
    response.say(
        "Hola. Esta llamada ha sido detectada como posible intento de cobro. Será grabada. Por favor, identifíquese.",
        voice="woman",
        language="es-ES"
    )
    response.record(
        action="/process-recording",
        method="POST",
        max_length=20,
        timeout=5,
        play_beep=True
    )
    return str(response)

@app.route("/process-recording", methods=["POST"])
def process_recording():
    recording_url = request.form.get("RecordingUrl")
    audio_file_path = "/tmp/recording.wav"

    # Descargamos el audio desde Twilio
    audio_data = requests.get(recording_url + ".wav").content
    with open(audio_file_path, "wb") as f:
        f.write(audio_data)

    # Transcripción con Whisper
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    text = transcript.text.strip()

    # Generación de respuesta con GPT
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que disuade llamadas de cobro falsas."},
            {"role": "user", "content": f"Mensaje del llamante: {text}"}
        ]
    )

    response_text = completion.choices[0].message.content

    # Respondemos al llamante
    response = VoiceResponse()
    response.say(response_text, voice="woman", language="es-ES")
    return str(response)

@app.route("/")
def home():
    return "Servidor Flask funcionando correctamente."
