
from fastapi import APIRouter, Response, HTTPException
from schemas import Note
from typing import List

router = APIRouter()

# Dummy notes data for now
NOTES = [
    Note(
        id="1",
        title="Sample Video Note",
        source_type="video",
        source_name="Lecture 1",
        created_at="2025-10-01",
        model_used="gemini",
        thumbnails=["/static/thumb1.png"],
        markdown_url="/notes/download/md/1",
        pdf_url="/notes/download/pdf/1"
    ),
    Note(
        id="2",
        title="Sample Document Note",
        source_type="document",
        source_name="Notes.pdf",
        created_at="2025-10-02",
        model_used="gemini",
        thumbnails=["/static/thumb2.png"],
        markdown_url="/notes/download/md/2",
        pdf_url="/notes/download/pdf/2"
    )
]

@router.get("/notes/", response_model=List[Note])
def get_notes():
    return NOTES


# Dummy PDF/Markdown download endpoints
@router.get("/notes/download/pdf/{note_id}")
def download_note_pdf(note_id: str):
    # In production, fetch and return the real PDF file
    for note in NOTES:
        if note.id == note_id:
            content = f"PDF content for note {note_id}".encode()
            return Response(content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={note.title}.pdf"})
    raise HTTPException(status_code=404, detail="Note not found")

@router.get("/notes/download/md/{note_id}")
def download_note_md(note_id: str):
    # In production, fetch and return the real Markdown file
    for note in NOTES:
        if note.id == note_id:
            content = f"# Markdown for note {note_id}\nSample content.".encode()
            return Response(content, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename={note.title}.md"})
    raise HTTPException(status_code=404, detail="Note not found")
