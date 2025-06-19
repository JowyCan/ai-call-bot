from flask import Flask, request
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

# Inicializar el cliente de OpenAI con la nueva API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def index():
    return "Servidor de AI Call Bot operativo."

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # Extraer los datos del número llamante
    from_number = request.values.get("From", "Desconocido")

    # Crear un mensaje basado en el número llamante
    messages = [
        {"role": "system", "content": "Eres un agente automático diseñado para disuadir llamadas sospechosas o de cobro."},
        {"role": "user", "content": f"Recibes una llamada sospechosa del número {from_number}. Responde con firmeza pero educación, en español, para disuadir al llamante."}
    ]

    # Llamada al modelo GPT-3.5-Turbo
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    # Obtener la respuesta generada
    ai_response = chat_response.choices[0].message.content.strip()

    # Crear la respuesta de voz de Twilio
    response = VoiceResponse()
    response.say(ai_response, voice="Polly.Conchita", language="es-ES")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
