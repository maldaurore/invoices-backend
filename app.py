import logging, sys
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()
logger.setLevel("INFO")

h_console = logging.StreamHandler(sys.stderr)
h_console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logger.addHandler(h_console)

h_file = RotatingFileHandler("app.log", maxBytes=10*1024*1024, backupCount=3, encoding="utf-8")
h_file.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logger.addHandler(h_file)

import os
from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename
import tempfile
from agents import Runner
from src.utils.paths import OUTPUT_DIR
from src.utils.setup_vector_db import setup_db

setup_db()

from src.main_agent import mainAgent
    
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL")}})
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")

@app.route("/health", methods=["GET"])
def health():
    try:
        _ = client.models.list()
        logger.info("OK: la key funciona")
        return {"ok": True}
    except Exception as e:
        logger.error("Fallo list models:", e)
        return {"ok": False, "error": str(e)}

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name.lower().endswith('.pdf'):
        abort(400, description="Nombre de archivo invalido.")
    
    full_path = os.path.abspath(os.path.join(OUTPUT_DIR, safe_name))
    logger.info(f"OUTPUT_DIR: {OUTPUT_DIR}")
    logger.info(f"full_path: {full_path}")

    if not full_path.startswith(OUTPUT_DIR):
        abort(400, description="Ruta invalida.")
        
    if not os.path.exists(full_path):
        logger.error(f"Archivo no encontrado: {full_path}")
        abort(404, description="Archivo no encontrado.")
    
    return send_from_directory(OUTPUT_DIR, safe_name, as_attachment=True, mimetype="application/pdf")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Espera multipart/form-data con el campo 'file' (audio/webm, audio/ogg, audio/mpeg, etc.)
    Opcionales:
      - lang (ej. 'es' o 'es-MX') -> algunos modelos autodetectan; lo pasamos como hint.
    """
    if "file" not in request.files:
        return jsonify({"error": "Falta el archivo (field 'file')"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Archivo vacío"}), 400

    filename = secure_filename(f.filename)
    # Guardar temporalmente
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, filename)
        f.save(path)

        # Llamada a la API de OpenAI Audio -> transcriptions
        with open(path, "rb") as audio:
            result = client.audio.transcriptions.create(
                model='whisper-1',
                file=audio,
            )
        return jsonify({"text": result.text}), 200


@app.route("/send-message", methods=["POST"])
async def sendMessage():
    data = request.get_json()
    
    chat_history = data.get('chatHistory', [])
    
    messages = [{ "role": message["role"], "content": message["content"] } for message in chat_history ]
    result = await Runner.run(
        mainAgent,
        messages
    )
    return jsonify({
        "message": result.final_output.texto,
        "archivo_generado": result.final_output.archivo_generado,
        "nombre_archivo": result.final_output.nombre_archivo
    })
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
