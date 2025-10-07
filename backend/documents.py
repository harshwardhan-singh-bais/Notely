from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from schemas import DocumentMeta
import os

router = APIRouter()

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
    # --- End integration ---

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
