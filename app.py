from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

from io import BytesIO
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    response = VoiceResponse()
    response.say("Hola. Esta llamada será grabada. Por favor, diga su mensaje después del tono.",
                 voice="Polly.Lucia", language="es-ES")
    response.record(
        action="/process-recording",
        method="POST",
        maxLength=10,
        timeout=1,
        transcribe=False,
        playBeep=True
    )
    return Response(str(response), mimetype="application/xml")

@app.route("/process-recording", methods=["POST"])
def process_recording():
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        return "No recording received", 400

    audio_url = recording_url + ".wav"
    audio_data = requests.get(audio_url).content
    audio_file = BytesIO(audio_data)

    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="es"
    ).text

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": transcript}],
        temperature=0.7
    )

    reply = completion.choices[0].message.content

    response = VoiceResponse()
    response.say(reply, voice="Polly.Lucia", language="es-ES")
    response.hangup()
    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
