from flask import Flask, request, Response
import openai
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Configura tu clave API de OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")
call_history = {}  # Guardará números que ya llamaron

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    caller_number = request.form.get("From")

    # Detectar llamadas repetidas
    if caller_number in call_history:
        prompt = f"""
Este número {caller_number} ya ha llamado anteriormente. Responde como un asistente legal que detecta acoso telefónico.
Indica de forma clara, legal y severa que esta llamada será denunciada por insistencia indebida y que se tomarán medidas.
Mantén un tono firme y respetuoso.
"""
    else:
        prompt = f"""
Recibes una llamada del número {caller_number}. Actúa como un asistente legal experto.
El objetivo es disuadir a la persona que llama, en caso de que sea un intento de fraude o cobro no justificado.

Tu respuesta debe ser firme, cortés, en tono legal y dejar claro que:
- No se reconoce la deuda.
- La llamada puede estar siendo grabada.
- Cualquier intento de coacción será denunciado.
- Se solicita no volver a llamar.

Responde con una voz tranquila y profesional.
"""
        call_history[caller_number] = 1

    # Llamar a la API de OpenAI
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente legal que responde llamadas de cobros falsos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    ai_reply = completion.choices[0].message["content"]
    print("Respuesta generada por la IA:", ai_reply)

    # Crear respuesta de voz para Twilio
    response = VoiceResponse()
    response.say(ai_reply, voice='alice', language='es-ES')

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



