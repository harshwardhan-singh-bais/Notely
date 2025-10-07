
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
from typing import List
from schemas import DocumentMeta
import os



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

# Dummy document metadata list
DOCUMENTS = [
    DocumentMeta(
        id="1",
        name="Notes.pdf",
        type="pdf",
        size=123456,
        uploaded_at="2025-10-02",
        status="processed"
    )
]

@router.post("/document/upload/", response_model=dict)
def upload_document(file: UploadFile = File(...)):
    # Save file to disk (dummy logic)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # --- Document text extraction integration ---
    try:
        import subprocess
        doc_id = str(len(DOCUMENTS)+1)
        extract_dir = os.path.join("extracted_text", doc_id)
        os.makedirs(extract_dir, exist_ok=True)
        extracted_txt = os.path.join(extract_dir, "extracted.txt")
        subprocess.run([
            "python", "extract_text_from_document.py", file_location, extracted_txt
        ], check=True)
    except Exception as e:
        print(f"[WARN] Document text extraction failed: {e}")

    # --- Gemini note generation integration ---
    try:
        notes_dir = os.path.join("notes", doc_id)
        os.makedirs(notes_dir, exist_ok=True)
        notes_md = os.path.join(notes_dir, "notes.md")
        import subprocess
        subprocess.run([
            "python", "generate_notes_gemini.py", extracted_txt, notes_md
        ], check=True)
    except Exception as e:
        print(f"[WARN] Gemini note generation failed: {e}")
    # --- End Gemini integration ---

    # Add to dummy list
    doc = DocumentMeta(
        id=doc_id,
        name=file.filename,
        type=file.filename.split('.')[-1],
        size=os.path.getsize(file_location),
        uploaded_at="2025-10-03",
        status="pending"
    )
    DOCUMENTS.append(doc)
    return {"document_id": doc.id}

@router.get("/document/list/", response_model=List[DocumentMeta])
def list_documents():
    return DOCUMENTS
