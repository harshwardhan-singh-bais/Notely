
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional
from schemas import JobStatus
import os
import uuid



router = APIRouter()

# Endpoint to serve generated notes for a video job
@router.get("/video/notes/{job_id}", response_class=PlainTextResponse)
def get_video_notes(job_id: str):
    notes_path = os.path.join("notes", job_id, "notes.md")
    if not os.path.exists(notes_path):
        raise HTTPException(status_code=404, detail="Notes not found for this job.")
    with open(notes_path, "r", encoding="utf-8") as f:
        return f.read()

# Endpoint to serve generated notes for a video job
@router.get("/video/notes/{job_id}", response_class=PlainTextResponse)
def get_video_notes(job_id: str):
    notes_path = os.path.join("notes", job_id, "notes.md")
    if not os.path.exists(notes_path):
        raise HTTPException(status_code=404, detail="Notes not found for this job.")
    with open(notes_path, "r", encoding="utf-8") as f:
        return f.read()

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dummy job status store
JOBS = {}

@router.post("/video/submit_job/", response_model=dict)
def submit_video_job(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    screenshot_interval: Optional[int] = Form(None),
    smart_mode: Optional[bool] = Form(False)
):
    job_id = str(uuid.uuid4())
    if file:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        source = file.filename
        # --- Smart screenshot extraction integration ---
        try:
            from extract_diagram_frames import extract_relevant_frames
            screenshots_dir = os.path.join("ai_screenshots", job_id)
            os.makedirs(screenshots_dir, exist_ok=True)
            extract_relevant_frames(file_location, screenshots_dir)
        except Exception as e:
            print(f"[WARN] Screenshot extraction failed: {e}")
        # --- End integration ---

        # --- Whisper transcription integration ---
        try:
            import subprocess
            transcript_dir = os.path.join("transcripts", job_id)
            os.makedirs(transcript_dir, exist_ok=True)
            transcript_txt = os.path.join(transcript_dir, "transcript.txt")
            transcript_json = os.path.join(transcript_dir, "transcript.json")
            subprocess.run([
                "python", "transcribe_whisper.py", file_location, transcript_txt
            ], check=True)
            # The script also saves a .json file by default
        except Exception as e:
            print(f"[WARN] Whisper transcription failed: {e}")
        # --- End transcription integration ---

        # --- Gemini note generation integration ---
        try:
            notes_dir = os.path.join("notes", job_id)
            os.makedirs(notes_dir, exist_ok=True)
            notes_md = os.path.join(notes_dir, "notes.md")
            # Optionally, add alignment path if available (e.g., after running align_srt_with_frames.py)
            alignment_path = None
            # If alignment file exists, use it
            possible_alignment = os.path.join(screenshots_dir, "frame_subtitle_alignment.json")
            if os.path.exists(possible_alignment):
                alignment_path = possible_alignment
            import subprocess
            subprocess.run([
                "python", "generate_notes_gemini.py", transcript_txt, notes_md
            ] + ([alignment_path] if alignment_path else []), check=True)
        except Exception as e:
            print(f"[WARN] Gemini note generation failed: {e}")
        # --- End Gemini integration ---
    elif url:
        source = url
    else:
        raise HTTPException(status_code=400, detail="No video file or URL provided.")
    # Add to dummy jobs
    JOBS[job_id] = JobStatus(job_id=job_id, status="pending")
    return {"job_id": job_id}

@router.get("/video/job_status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
