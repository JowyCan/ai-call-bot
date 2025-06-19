from flask import Flask, request, Response
from flask_cors import CORS
import openai
from twilio.twiml.voice_response import VoiceResponse
import os
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir peticiones CORS si haces pruebas desde frontend

# Clave API de OpenAI desde Render (variable de entorno)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Ruta de prueba
@app.route("/", methods=["GET", "POST"])
def index():
    return "AI Call Bot operativo en /incoming-call"

# Ruta principal para llamadas de Twilio
@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    try:
        caller_number = request.form.get("From", "desconocido")
        print(f"📞 Llamada recibida de: {caller_number}")

        # Prompt a OpenAI
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

        # Recorte de respuesta si es muy larga (Twilio puede fallar con >450 caracteres)
        max_length = 450
        if len(ai_reply) > max_length:
            ai_reply = ai_reply[:max_length].rsplit('.', 1)[0] + '.'

        print("✅ Respuesta generada por la IA:", ai_reply)

        # Guardar log en CSV (opcional)
        with open("call_log.csv", "a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), caller_number, ai_reply])

        # Crear respuesta de voz
        response = VoiceResponse()
        response.say(ai_reply, voice='Polly.Conchita', language='es-ES')

        return Response(str(response), mimetype='text/xml')

    except Exception as e:
        print("❌ ERROR en la llamada:", e)
        # Mensaje alternativo si falla la IA
        fallback_response = VoiceResponse()
        fallback_response.say(
            "Esta llamada no ha sido autorizada. Absténgase de insistir. Gracias.",
            voice='Polly.Conchita',
            language='es-ES'
        )
        return Response(str(fallback_response), mimetype='text/xml')

# Puerto dinámico para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
