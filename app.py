from flask import Flask, request, Response
import openai
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Configura tu clave API de OpenAI y Twilio
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Ruta que Twilio usará como webhook para llamadas entrantes
@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # Puedes obtener más info como: request.form['From'], etc.
    caller_number = request.form.get("From")

    # Mensaje base al que la IA puede responder
    prompt = f"Un cobrador sospechoso ha llamado desde {caller_number}. Genera una respuesta firme, legal, educada y disuasiva."

    # Llama a la API de OpenAI (puedes ajustar el modelo y parámetros)
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente legal que responde llamadas de cobros falsos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    ai_reply = completion.choices[0].message["content"]

    # Crea la respuesta de voz para Twilio
    response = VoiceResponse()
    response.say(ai_reply, voice='alice', language='es-ES')

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
