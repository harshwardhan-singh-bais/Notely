
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
from typing import List
from schemas import DocumentMeta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Endpoint to serve generated notes for a document
@router.get("/document/notes/{doc_id}", response_class=PlainTextResponse)
def get_document_notes(doc_id: str):
    notes_path = os.path.join("notes", doc_id, "notes.md")
    if not os.path.exists(notes_path):
        raise HTTPException(status_code=404, detail="Notes not found for this document.")
    with open(notes_path, "r", encoding="utf-8") as f:
        return f.read()

# Endpoint to serve generated notes for a document
@router.get("/document/notes/{doc_id}", response_class=PlainTextResponse)
def get_document_notes(doc_id: str):
    notes_path = os.path.join("notes", doc_id, "notes.md")
    if not os.path.exists(notes_path):
        raise HTTPException(status_code=404, detail="Notes not found for this document.")
    with open(notes_path, "r", encoding="utf-8") as f:
        return f.read()

UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Real document metadata - scan from actual uploads
def get_real_documents():
    """Scan uploaded documents and return actual metadata"""
    documents = []
    if not os.path.exists(UPLOAD_DIR):
        return documents
    
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            # Get file stats
            stat = os.stat(file_path)
            import datetime
            uploaded_date = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d")
            
            # Determine document ID (look for corresponding extracted text or notes)
            doc_id = None
            for potential_id in os.listdir("extracted_text") if os.path.exists("extracted_text") else []:
                if os.path.exists(os.path.join("extracted_text", potential_id)):
                    doc_id = potential_id
                    break
            
            if not doc_id:
                doc_id = str(len(documents) + 1)
            
            # Check processing status
            status = "pending"
            if os.path.exists(os.path.join("notes", doc_id, "notes.md")):
                status = "processed"
            elif os.path.exists(os.path.join("extracted_text", doc_id)):
                status = "processing"
            
            documents.append(DocumentMeta(
                id=doc_id,
                name=filename,
                type=os.path.splitext(filename)[1][1:] if '.' in filename else "unknown",
                size=stat.st_size,
                uploaded_at=uploaded_date,
                status=status
            ))
    return documents

@router.get("/document/list/", response_model=List[DocumentMeta])
def get_documents():
    return get_real_documents()

from pydantic import BaseModel

class ProgressUpdate(BaseModel):
    progress: int  # 0-100
    stage: str
    message: str

# In-memory progress tracking
PROGRESS_TRACKER = {}

@router.get("/document/progress/{doc_id}")
def get_document_progress(doc_id: str):
    return PROGRESS_TRACKER.get(doc_id, {"progress": 0, "stage": "pending", "message": "Not started"})

def update_progress(doc_id: str, progress: int, stage: str, message: str):
    PROGRESS_TRACKER[doc_id] = {"progress": progress, "stage": stage, "message": message}

@router.post("/document/upload/", response_model=dict)
def upload_document(file: UploadFile = File(...)):
    import subprocess
    from fastapi import status
    # Generate unique document ID
    import time
    doc_id = str(int(time.time()))
    
    update_progress(doc_id, 5, "uploading", "Saving uploaded file...")
    
    # Save file to disk
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    update_progress(doc_id, 20, "extracting", "Extracting text from document...")
    
    error_messages = []
    extract_dir = os.path.join("extracted_text", doc_id)
    os.makedirs(extract_dir, exist_ok=True)
    extracted_txt = os.path.join(extract_dir, "extracted.txt")
    # --- Document text extraction integration ---
    try:
        result = subprocess.run([
            "python", "extract_text_from_document.py", file_location, extracted_txt
        ], check=True, capture_output=True, text=True)
        update_progress(doc_id, 50, "generating", "Generating notes with Gemini...")
    except subprocess.CalledProcessError as e:
        error_msg = f"Document text extraction failed: {e.stderr or e.stdout or str(e)}"
        error_messages.append(error_msg)
    except Exception as e:
        error_msg = f"Document text extraction failed: {str(e)}"
        error_messages.append(error_msg)

    # --- Gemini note generation integration ---
    notes_dir = os.path.join("notes", doc_id)
    os.makedirs(notes_dir, exist_ok=True)
    notes_md = os.path.join(notes_dir, "notes.md")
    try:
        result = subprocess.run([
            "python", "generate_notes_gemini.py", extracted_txt, notes_md
        ], check=True, capture_output=True, text=True)
        update_progress(doc_id, 100, "completed", "Notes generated successfully!")
    except subprocess.CalledProcessError as e:
        error_msg = f"Gemini note generation failed: {e.stderr or e.stdout or str(e)}"
        error_messages.append(error_msg)
    except Exception as e:
        error_msg = f"Gemini note generation failed: {str(e)}"
        error_messages.append(error_msg)
    # --- End Gemini integration ---

    if error_messages:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="; ".join(error_messages))

    return {"document_id": doc_id, "message": "Document processed successfully", "filename": file.filename}

@router.get("/document/list/", response_model=List[DocumentMeta])
def list_documents():
    return get_real_documents()
