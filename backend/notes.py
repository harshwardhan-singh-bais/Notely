
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from schemas import Note
from typing import List
import os

router = APIRouter()

class NoteGenerationRequest(BaseModel):
    source_id: str
    source_type: str  # "video" or "document"

# Real notes data - scanned from actual files
def get_real_notes():
    """Scan the notes directory and return actual notes"""
    notes = []
    notes_dir = "notes"
    if not os.path.exists(notes_dir):
        return notes
    
    for note_id in os.listdir(notes_dir):
        note_path = os.path.join(notes_dir, note_id)
        if os.path.isdir(note_path):
            notes_file = os.path.join(note_path, "notes.md")
            if os.path.exists(notes_file):
                # Determine source type based on what directories exist
                source_type = "document"  # default
                source_name = f"Document {note_id}"
                
                # Check if this is from a video job
                if os.path.exists(os.path.join("transcripts", note_id)):
                    source_type = "video"
                    source_name = f"Video {note_id}"
                elif os.path.exists(os.path.join("extracted_text", note_id)):
                    source_type = "document"
                    source_name = f"Document {note_id}"
                
                # Get creation time
                created_at = os.path.getctime(notes_file)
                import datetime
                created_date = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d")
                
                notes.append(Note(
                    id=note_id,
                    title=f"Notes for {source_name}",
                    source_type=source_type,
                    source_name=source_name,
                    created_at=created_date,
                    model_used="gemini",
                    thumbnails=[],
                    markdown_url=f"/notes/download/md/{note_id}",
                    pdf_url=f"/notes/download/pdf/{note_id}"
                ))
    return notes

@router.get("/notes/", response_model=List[Note])
def get_notes():
    return get_real_notes()

@router.post("/notes/generate/")
def generate_notes(request: NoteGenerationRequest):
    """Generate notes from an existing video job or document"""
    source_id = request.source_id
    source_type = request.source_type
    
    # Check if notes already exist for this source
    notes_path = None
    if source_type == "video":
        notes_path = os.path.join("notes", source_id, "notes.md")
    elif source_type == "document":
        notes_path = os.path.join("notes", source_id, "notes.md")
    
    if notes_path and os.path.exists(notes_path):
        # Notes already exist
        return {"note_id": source_id, "message": "Notes already generated"}
    else:
        # Notes don't exist yet - they should be generated during upload/processing
        raise HTTPException(status_code=404, detail=f"Notes not found for {source_type} {source_id}. Please ensure the {source_type} was processed correctly.")


# Real PDF/Markdown download endpoints
@router.get("/notes/download/pdf/{note_id}")
def download_note_pdf(note_id: str):
    # In production, fetch and return the real PDF file
    notes = get_real_notes()
    for note in notes:
        if note.id == note_id:
            content = f"PDF content for note {note_id}".encode()
            return Response(content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={note.title}.pdf"})
    raise HTTPException(status_code=404, detail="Note not found")

@router.get("/notes/download/md/{note_id}")
def download_note_md(note_id: str):
    # Return the actual markdown file
    notes = get_real_notes()
    for note in notes:
        if note.id == note_id:
            notes_file = os.path.join("notes", note_id, "notes.md")
            if os.path.exists(notes_file):
                with open(notes_file, "r", encoding="utf-8") as f:
                    content = f.read()
                return Response(content, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename={note.title}.md"})
    raise HTTPException(status_code=404, detail="Note not found")
