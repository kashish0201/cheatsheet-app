from typing import Dict
from uuid import uuid4

UPLOAD_STORE: Dict[str, dict] = {}

def create_upload_session():
    upload_id = str(uuid4())

    UPLOAD_STORE[upload_id] = {
        "files": [],
        "combined_text": ""
    }

    return upload_id


def add_file(upload_id: str, filename: str, text: str):
    UPLOAD_STORE[upload_id]["files"].append(filename)
    UPLOAD_STORE[upload_id]["combined_text"] += "\n" + text


def get_upload(upload_id: str):
    return UPLOAD_STORE.get(upload_id)
