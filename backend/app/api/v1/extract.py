from fastapi import APIRouter
from app.utils.extractors import extract_text_from_pdf, extract_text_from_pptx
import os

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/extract")
def extract_text(filename:str):
    file_path = os.path.join(UPLOAD_DIR,filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    if filename.endswith(".pptx"):
        text = extract_text_from_pptx(file_path)
    elif filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        return {"error": "Unsupported file type"}
    

    return {
        "filename": filename,
        "text": text[:3000]  # limit for now
    }