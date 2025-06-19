from flask import Flask, request, Response
import openai
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Clave API de OpenAI desde Render (variable de entorno)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return "AI Call Bot operativo en /incoming-call"

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    try:
        # Obtener número del llamante
        caller_number = request.form.get("From")

        # Prompt detallado para la IA
        prompt = f"""
Recibes una llamada del número {caller_number}. Actúa como un asistente legal experto.

Tu objetivo es disuadir educadamente a la persona que llama si se trata de un intento de cobro fraudulento o no justificado.

Responde con firmeza, cortesía y en tono legal, dejando claro que:
- No se reconoce ninguna deuda.
- Esta llamada puede estar siendo grabada.
- Cualquier intento de coacción será denunciado.
- Se solicita que no vuelvan a contactar por este medio.

Tu tono debe ser profesional y tranquilo. Responde directamente como si hablaras por teléfono.
"""

        # Llamada a OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente legal telefónico que responde llamadas sospechosas. Siempre hablas en español."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        ai_reply = completion.choices[0].message["content"]
        print("✅ Respuesta generada por la IA:", ai_reply)

        # Crear respuesta de voz con Twilio
        response = VoiceResponse()
        response.say(ai_reply, voice='Polly.Conchita', language='es-ES')

        return Response(str(response), mimetype='text/xml')

    except Exception as e:
        print("❌ ERROR en la llamada:", e)
        return "Error interno", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




