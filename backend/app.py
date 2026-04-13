import os
import uuid
import traceback
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "meta-llama/llama-3-8b-instruct")


@app.route("/")
def home():
    return {"message": "Cheat Sheet backend is running"}


@app.route("/api/health")
def health():
    return {"status": "ok"}


@app.route("/api/v1/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    upload_id = request.form.get("upload_id")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # Reuse existing session if upload_id is provided
    if upload_id:
        folder = UPLOAD_DIR / upload_id
        folder.mkdir(parents=True, exist_ok=True)
    else:
        upload_id = str(uuid.uuid4())
        folder = UPLOAD_DIR / upload_id
        folder.mkdir(parents=True, exist_ok=True)

    saved_files = []
    existing_names = {f.name for f in folder.iterdir() if f.is_file()}

    for file in files:
        if file and file.filename:
            filename = file.filename.strip()

            # skip duplicates by filename
            if filename in existing_names:
                continue

            save_path = folder / filename
            file.save(save_path)
            saved_files.append(filename)
            existing_names.add(filename)

    all_files = sorted([f.name for f in folder.iterdir() if f.is_file()])

    return jsonify({
        "message": f"{len(saved_files)} new file(s) uploaded successfully",
        "upload_id": upload_id,
        "files": all_files
    }), 200


@app.route("/api/v1/cheatsheet", methods=["POST"])
def generate_cheatsheet():
    try:
        data = request.get_json(silent=True) or {}
        upload_id = data.get("upload_id")

        if not upload_id:
            return jsonify({"error": "upload_id is required"}), 400

        folder = UPLOAD_DIR / upload_id
        if not folder.exists():
            return jsonify({"error": "Invalid upload_id"}), 404

        files = [f for f in folder.iterdir() if f.is_file()]
        if not files:
            return jsonify({"error": "No files found"}), 400

        combined_text = ""
        for file_path in files:
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = f"[Could not read {file_path.name} as plain text]"

            combined_text += f"\n\n===== FILE: {file_path.name} =====\n{text}"

        prompt = f"""
Create a clean, structured cheat sheet from these uploaded files.

Requirements:
- Add a title
- Use headings
- Use bullet points
- Include key concepts
- Include a short summary

Content:
{combined_text[:12000]}
""".strip()

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            max_output_tokens=1200
        )

        return jsonify({
            "cheatsheet": response.output_text
        }), 200

    except Exception as e:
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return jsonify({
            "error": "Failed to generate cheat sheet",
            "details": str(e)
        }), 500

@app.route("/api/v1/reset", methods=["POST"])
def reset_upload_session():
    data = request.get_json(silent=True) or {}
    upload_id = data.get("upload_id")

    if not upload_id:
        return jsonify({"message": "Nothing to reset"}), 200

    folder = UPLOAD_DIR / upload_id
    if folder.exists() and folder.is_dir():
        for file_path in folder.iterdir():
            if file_path.is_file():
                file_path.unlink()
        folder.rmdir()

    return jsonify({"message": "Session reset successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)