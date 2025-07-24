from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import os
from dotenv import load_dotenv
import tempfile
from typing import Optional
import base64
import re
def clean_llm_json_response(text: str) -> str:
    """Remove code fences and extra whitespace from LLM output."""
    # Remove triple backticks and optional 'json' after them
    text = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'```$', '', text.strip())
    # Remove any leading/trailing whitespace again
    return text.strip()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


from pdf2image import convert_from_path
import pytesseract
import docx
import pdfplumber
from app.llm_provider import get_llm
from app.prompt_utils import build_contract_classification_prompt
from app.models import ContractTypePrediction
from app.contract_types import CONTRACT_TYPES



load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AES-256 key (should be 32 bytes). In production, load from env or secure vault.
AES_KEY = os.environ.get("ACIO_AES_KEY", "0123456789abcdef0123456789abcdef").encode()[:32]
AES_IV = b"acioinitvector12"  # 16 bytes for AES CBC

def encrypt_bytes(data: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()

def decrypt_bytes(data: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()


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


def get_valid_contract_types():
    return {ct["name"] for ct in CONTRACT_TYPES}



@app.post("/extract-text/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read file bytes
        file_bytes = await file.read()
        # Encrypt and save to disk
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            encrypted = encrypt_bytes(file_bytes)
            tmp.write(encrypted)
            tmp_path = tmp.name
        # Decrypt in memory for processing
        with open(tmp_path, "rb") as f:
            decrypted_bytes = decrypt_bytes(f.read())
        # Save decrypted to another temp file for extraction
        with tempfile.NamedTemporaryFile(delete=False) as dec_tmp:
            dec_tmp.write(decrypted_bytes)
            dec_tmp_path = dec_tmp.name
        text = extract_text(dec_tmp_path, file.filename) # type: ignore
        os.unlink(tmp_path)
        os.unlink(dec_tmp_path)
        return JSONResponse(content={"text": text})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Contract Type Classification Endpoint ---
@app.post("/classify-contract/")
async def classify_contract(
    file: UploadFile = File(...),
    provider: str = Query("openai", description="LLM provider: 'openai' or 'groq'")
):
    try:
        # Extract text from file (reuse FR-01 logic)
        file_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            encrypted = encrypt_bytes(file_bytes)
            tmp.write(encrypted)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            decrypted_bytes = decrypt_bytes(f.read())
        with tempfile.NamedTemporaryFile(delete=False) as dec_tmp:
            dec_tmp.write(decrypted_bytes)
            dec_tmp_path = dec_tmp.name
        contract_text = extract_text(dec_tmp_path, file.filename) # type: ignore
        os.unlink(tmp_path)
        os.unlink(dec_tmp_path)

        # Build prompt
        prompt = build_contract_classification_prompt(contract_text)

        # Call LLM
        llm = get_llm(provider)
        response = llm.invoke(prompt)
        print(type(response), type(response.content))
        # If using LangChain, response may be a BaseMessage or string
        if hasattr(response, 'content'):
            response_content = response.content
        else:
            response_content = response        

        # Parse and validate structured output
        if not isinstance(response_content, (str, bytes, bytearray)):
            # Try to convert to string, else error
            try:
                # print(response_content)
                response_content = str(response_content)
            except Exception:
                # print("Line 173")
                raise HTTPException(status_code=422, detail="LLM response is not a valid string.")
        try:
            # print(response_content)
            cleaned = clean_llm_json_response(response_content)
            # If cleaned is a plain string (not JSON), wrap it
            import json
            try:
                # Try to parse as JSON
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict):
                    result = ContractTypePrediction.model_validate_json(cleaned)
                elif isinstance(parsed, str):
                    # LLM returned just the contract type string
                    result = ContractTypePrediction.model_validate_json(json.dumps({"contract_type": parsed}))
                else:
                    raise ValueError("Unexpected LLM output format.")
            except json.JSONDecodeError:
                # Not JSON, treat as plain string
                result = ContractTypePrediction.model_validate_json(json.dumps({"contract_type": cleaned}))
        except ValidationError:
            # print("Line 179")
            raise HTTPException(status_code=422, detail="LLM did not return valid structured output.")

        valid_types = get_valid_contract_types()
        if result.contract_type not in valid_types:
            result.contract_type = "Unknown"

        return result.model_dump()
    except Exception as e:
        # print("Line 188")
        raise HTTPException(status_code=400, detail=str(e))


