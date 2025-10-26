from flask import Flask, make_response, request, send_file
from flask_cors import CORS
import subprocess
import os

print("Starting Flask server...")

app = Flask(__name__)
CORS(app)  # allow all origins


VOICE_MODEL = "voices/es_MX-claude-high.onnx"  # relative to server.py
OUTPUT_FILE = "output.wav"

@app.route("/tts", methods=["POST"])
def tts():
    text = request.json.get("text", "")
    if not text:
        return {"error": "No text provided"}, 400

    # Run Piper
    cmd = [
        "piper",
        "--model", VOICE_MODEL,
        "--output-file", OUTPUT_FILE
    ]

    subprocess.run(cmd, input=text.encode("utf-8"), check=True)

    # Make sure the file exists
    if not os.path.exists(OUTPUT_FILE):
        return {"error": "Audio file not found"}, 500

    # Send the audio file
    return send_file(
        OUTPUT_FILE,
        mimetype="audio/wav",
        as_attachment=False,  # important for inline playback
        conditional=False     # disables range requests (safer for blobs)
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
