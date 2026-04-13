from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import shutil
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    saved_files = []

    for file in files:
        unique_name = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file.filename)

    return {
        "files": saved_files,
        "message": "Files uploaded successfully"
    }
