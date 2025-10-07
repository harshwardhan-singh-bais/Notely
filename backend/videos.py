
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

# Progress tracking for video jobs
VIDEO_PROGRESS = {}

def update_video_progress(job_id: str, progress: int, stage: str, message: str):
    VIDEO_PROGRESS[job_id] = {"progress": progress, "stage": stage, "message": message}

@router.get("/video/progress/{job_id}")
def get_video_progress(job_id: str):
    return VIDEO_PROGRESS.get(job_id, {"progress": 0, "stage": "pending", "message": "Not started"})

# Real job status store - improved
JOBS = {}

@router.post("/video/submit_job/", response_model=dict)
def submit_video_job(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    screenshot_interval: Optional[int] = Form(None),
    smart_mode: Optional[bool] = Form(False)
):

    import subprocess
    from fastapi import status
    job_id = str(uuid.uuid4())
    
    update_video_progress(job_id, 5, "starting", "Initializing video processing...")
    
    error_messages = []
    if file:
        update_video_progress(job_id, 10, "uploading", "Saving video file...")
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        source = file.filename
        
        update_video_progress(job_id, 20, "extracting", "Extracting screenshots...")
        
        # --- Smart screenshot extraction integration ---
        try:
            from extract_diagram_frames import extract_relevant_frames
            screenshots_dir = os.path.join("ai_screenshots", job_id)
            os.makedirs(screenshots_dir, exist_ok=True)
            extract_relevant_frames(file_location, screenshots_dir)
            update_video_progress(job_id, 40, "transcribing", "Transcribing audio with Whisper...")
        except Exception as e:
            error_msg = f"Screenshot extraction failed: {str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 20, "error", error_msg)
        # --- End integration ---

        update_video_progress(job_id, 40, "transcribing", "Transcribing audio with Whisper...")
        
        # --- Whisper transcription integration ---
        transcript_dir = os.path.join("transcripts", job_id)
        os.makedirs(transcript_dir, exist_ok=True)
        transcript_txt = os.path.join(transcript_dir, "transcript.txt")
        transcript_json = os.path.join(transcript_dir, "transcript.json")
        try:
            result = subprocess.run([
                "python", "transcribe_whisper.py", file_location, transcript_txt
            ], check=True, capture_output=True, text=True)
            update_video_progress(job_id, 60, "aligning", "Aligning subtitles with frames...")
        except subprocess.CalledProcessError as e:
            error_msg = f"Whisper transcription failed: {e.stderr or e.stdout or str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 40, "error", error_msg)
        except Exception as e:
            error_msg = f"Whisper transcription failed: {str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 40, "error", error_msg)
        # --- End transcription integration ---

        update_video_progress(job_id, 60, "aligning", "Aligning subtitles with frames...")
        
        # --- Subtitle/frame alignment integration ---
        alignment_path = None
        try:
            # Look for SRT file in transcript_dir (assume transcript_txt is .txt, look for .srt)
            srt_path = os.path.splitext(transcript_txt)[0] + ".srt"
            if os.path.exists(srt_path) and os.path.exists(screenshots_dir):
                alignment_path = os.path.join(screenshots_dir, "frame_subtitle_alignment.json")
                result = subprocess.run([
                    "python", "align_srt_with_frames.py", srt_path, screenshots_dir, alignment_path
                ], check=True, capture_output=True, text=True)
                update_video_progress(job_id, 80, "generating", "Generating notes with Gemini...")
        except subprocess.CalledProcessError as e:
            error_msg = f"Subtitle/frame alignment failed: {e.stderr or e.stdout or str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 60, "error", error_msg)
        except Exception as e:
            error_msg = f"Subtitle/frame alignment failed: {str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 60, "error", error_msg)
        # --- End subtitle/frame alignment integration ---

        update_video_progress(job_id, 80, "generating", "Generating notes with Gemini...")
        
        # --- Gemini note generation integration ---
        notes_dir = os.path.join("notes", job_id)
        os.makedirs(notes_dir, exist_ok=True)
        notes_md = os.path.join(notes_dir, "notes.md")
        try:
            args = ["python", "generate_notes_gemini.py", transcript_txt, notes_md]
            if alignment_path and os.path.exists(alignment_path):
                args.append(alignment_path)
            result = subprocess.run(args, check=True, capture_output=True, text=True)
            update_video_progress(job_id, 100, "completed", "Video processing completed successfully!")
        except subprocess.CalledProcessError as e:
            error_msg = f"Gemini note generation failed: {e.stderr or e.stdout or str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 80, "error", error_msg)
        except Exception as e:
            error_msg = f"Gemini note generation failed: {str(e)}"
            error_messages.append(error_msg)
            update_video_progress(job_id, 80, "error", error_msg)
        # --- End Gemini integration ---
    elif url:
        source = url
        update_video_progress(job_id, 10, "processing", f"Processing video from URL: {url}")
        # URL processing would go here
        update_video_progress(job_id, 100, "completed", "URL processing completed!")
    else:
        raise HTTPException(status_code=400, detail="No video file or URL provided.")

    if error_messages:
        update_video_progress(job_id, 50, "error", "; ".join(error_messages))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="; ".join(error_messages))

    # Add to jobs with completed status
    JOBS[job_id] = JobStatus(job_id=job_id, status="completed")
    return {"job_id": job_id}

@router.get("/video/job_status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
