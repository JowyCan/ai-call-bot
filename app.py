import os
import requests
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    response = VoiceResponse()
    response.say("Hola. Esta llamada ha sido detectada como posible intento de cobro. Será grabada. Por favor, identifíquese.", voice="woman", language="es-ES")
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

    # Descargar el audio
    audio_data = requests.get(recording_url + ".wav").content
    with open(audio_file_path, "wb") as f:
        f.write(audio_data)

    # Transcribir con Whisper
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    text = transcript.text.strip()

    # Generar respuesta con GPT
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que disuade llamadas de cobro falsas."},
            {"role": "user", "content": f"Mensaje del llamante: {text}"}
        ]
    )

    response_text = completion.choices[0].message.content

    # Responder por voz al llamante
    response = VoiceResponse()
    response.say(response_text, voice="woman", language="es-ES")
    return str(response)

@app.route("/")
def home():
    return "Servidor Flask funcionando correctamente."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
