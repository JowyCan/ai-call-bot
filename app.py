import os
import requests
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai

# Configurar clave de API
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Servidor de voz IA funcionando."

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    response = VoiceResponse()

    # Mensaje inicial sin pulsar teclas
    response.say("Hola. Esta llamada está siendo analizada. Por favor, espere.", language="es-ES", voice="Polly.Conchita")

    # Grabar la voz del llamante
    response.record(
        action="/process-recording",
        max_length=10,
        transcribe=False,
        play_beep=True
    )
    return str(response)

@app.route("/process-recording", methods=["POST"])
def process_recording():
    recording_url = request.form["RecordingUrl"]
    audio_url = f"{recording_url}.wav"

    # Descargar el audio
    audio_data = requests.get(audio_url).content
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data)

    # Transcripción
    with open("temp_audio.wav", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Respuesta IA
    chat_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres una IA que disuade llamadas de cobro con tono serio pero respetuoso."},
            {"role": "user", "content": transcript["text"]}
        ],
        temperature=0.7
    )

    final_response = chat_response["choices"][0]["message"]["content"]

    # Responder con voz
    twilio_response = VoiceResponse()
    twilio_response.say(final_response, language="es-ES", voice="Polly.Conchita")

    return str(twilio_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
