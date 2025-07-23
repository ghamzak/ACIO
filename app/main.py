from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Optional

from pdf2image import convert_from_path
import pytesseract
import docx
import pdfplumber

app = FastAPI()


def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_scanned_pdf(file_path: str) -> str:
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text


def is_scanned_pdf(file_path: str) -> bool:
    # Heuristic: if pdfplumber can't extract text, treat as scanned
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                return False
    return True


def extract_text(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".pdf":
        if is_scanned_pdf(file_path):
            return extract_text_from_scanned_pdf(file_path)
        else:
            return extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return pytesseract.image_to_string(file_path)
    else:
        raise ValueError("Unsupported file type")


@app.post("/extract-text/")
async def upload_file(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        text = extract_text(tmp_path, file.filename)
        os.unlink(tmp_path)
        return JSONResponse(content={"text": text})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
