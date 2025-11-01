import glob
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
import subprocess
import os
import atexit
import time

print("Starting Flask server...")

app = Flask(__name__)
CORS(app)  # allow all origins

# VOICE_MODEL = "voices/es_AR-daniela-high.onnx"  # relative to server.py
VOICE_MODEL = "voices/es_MX-claude-high.onnx"  # relative to server.py
DB_FILE = "tts_db.txt"
WAV_PATTERN = "output*.wav"

# Config
LIBRE_PORT = 5600
LIBRE_CONTAINER_NAME = "libretranslate_local"
LIBRE_IMAGE = "libretranslate/libretranslate:latest"

def clear_existing_files():
    # Delete WAV files
    for wav_file in glob.glob(WAV_PATTERN):
        os.remove(wav_file)
    # Clear text DB
    open(DB_FILE, "w").close()

import requests
# TTS endpoint
@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text_field = data.get("text", "")
    delimiter = data.get("delimiter", ",")
    speed = float(data.get("speed", 1.0))

    if not text_field:
        return {"error": "No text provided"}, 400

    # Split text into list
    text_list = [t.strip() for t in text_field.split(delimiter) if t.strip()]
    if not text_list:
        return {"error": "No valid text entries found"}, 400

    generated_files = []

    with open(DB_FILE, "a") as db:
        for idx, entry in enumerate(text_list, start=1):
            output_file = f"output{idx}.wav"

            # Run Piper
            try:
                subprocess.run(
                    ["piper", "--model", VOICE_MODEL, "--output-file", output_file],
                    input=entry.encode("utf-8"),
                    check=True
                )
            except subprocess.CalledProcessError as e:
                return jsonify({"error": f"Piper failed: {e}"}), 500

            # Translate Spanish -> English
            try:
                r = requests.post(
                    f"http://localhost:{LIBRE_PORT}/translate",
                    data={
                        "q": entry,
                        "source": "es",
                        "target": "en"
                    }
                )
                r.raise_for_status()
                translated_text = r.json().get("translatedText", "")
            except Exception as e:
                translated_text = f"Translation error: {e}"

            # Save to DB
            db.write(f"{entry}{delimiter} {output_file}{delimiter} {translated_text}\n")
            generated_files.append(output_file)

    return jsonify({
        "status": "success",
        "generated_files": generated_files,
        "message": "Process completed"
    })

@app.route("/getdb", methods=["GET"])
def get_db():
    if not os.path.exists(DB_FILE):
        return jsonify({"error": "Database file not found"}), 404

    with open(DB_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    return jsonify({"db": lines})


# GET endpoint to serve a specific WAV file
@app.route("/getaudio<int:file_id>", methods=["GET"])
def get_audio(file_id):
    filename = f"output{file_id}.wav"
    if not os.path.exists(filename):
        return jsonify({"error": "File not found"}), 404
    return send_file(
        filename,
        mimetype="audio/wav",
        as_attachment=False,
        conditional=False
    )


# # Endpoint to serve the audio file
# @app.route("/audio", methods=["GET"])
# def get_audio():
#     if not os.path.exists(OUTPUT_FILE):
#         return {"error": "Audio not found"}, 404
#     return send_file(
#         OUTPUT_FILE,
#         mimetype="audio/wav",
#         as_attachment=False,
#         conditional=False
#     )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
