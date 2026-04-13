from fastapi import APIRouter, HTTPException
import os
from app.api.v1.extract import extract_text
from app.services.ai_service import generate_cheatsheet

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/cheatsheet")
async def create_cheatsheet():
    if not os.path.exists(UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    files = os.listdir(UPLOAD_DIR)
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    combined_text = ""

    for filename in files:
        file_path = os.path.join(UPLOAD_DIR, filename)
        text = extract_text(file_path)
        combined_text += "\n" + text

    if not combined_text.strip():
        raise HTTPException(status_code=400, detail="No readable content")


    cheatsheet = generate_cheatsheet(combined_text)

    return {
        "cheatsheet": cheatsheet,
        "files": os.listdir(UPLOAD_DIR)
    }
