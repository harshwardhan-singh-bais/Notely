
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

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ensure other directories exist
os.makedirs("ai_screenshots", exist_ok=True)
os.makedirs("transcripts", exist_ok=True)
os.makedirs("notes", exist_ok=True)

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
    import threading
    from fastapi import status
    
    job_id = str(uuid.uuid4())
    
    # Add to jobs with pending status initially
    JOBS[job_id] = JobStatus(job_id=job_id, status="pending")
    
    # Process in background thread
    def process_video():
        try:
            update_video_progress(job_id, 5, "starting", "Initializing video processing...")
            
            error_messages = []
            file_location = None
            
            if file:
                # Handle file upload
                update_video_progress(job_id, 10, "uploading", "Saving video file...")
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                
                # Create a safe filename without special characters
                import re
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file.filename)
                safe_filename = f"{job_id}_{safe_filename}"
                file_location = os.path.join(UPLOAD_DIR, safe_filename)
                
                with open(file_location, "wb") as f:
                    content = file.file.read()
                    f.write(content)
                source = safe_filename
                
            elif url:
                # Handle YouTube URL download
                update_video_progress(job_id, 10, "downloading", "Downloading video from URL...")
                try:
                    import yt_dlp
                    os.makedirs(UPLOAD_DIR, exist_ok=True)
                    
                    # Create a safe output filename
                    safe_job_filename = f"{job_id}_video.%(ext)s"
                    
                    # Configure yt-dlp options
                    ydl_opts = {
                        'outtmpl': os.path.join(UPLOAD_DIR, safe_job_filename),
                        'format': 'best[height<=720]',  # Download reasonable quality
                        'restrictfilenames': True,  # Use only ASCII characters
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        # Find the downloaded file
                        for file_path in os.listdir(UPLOAD_DIR):
                            if file_path.startswith(job_id):
                                file_location = os.path.join(UPLOAD_DIR, file_path)
                                break
                    
                    if not file_location or not os.path.exists(file_location):
                        raise Exception("Downloaded file not found")
                    
                    source = url
                    update_video_progress(job_id, 20, "extracting", "Video downloaded successfully, extracting screenshots...")
                    
                except Exception as e:
                    error_msg = f"YouTube download failed: {str(e)}"
                    error_messages.append(error_msg)
                    update_video_progress(job_id, 10, "error", error_msg)
                    return
            else:
                update_video_progress(job_id, 0, "error", "No video file or URL provided")
                return
            
            # Extract screenshots using AI
            update_video_progress(job_id, 20, "extracting", "Extracting intelligent screenshots...")
            screenshots_dir = os.path.join("ai_screenshots", job_id)
            try:
                from extract_diagram_frames import extract_relevant_frames
                os.makedirs(screenshots_dir, exist_ok=True)
                extract_relevant_frames(file_location, screenshots_dir)
                update_video_progress(job_id, 40, "transcribing", "Screenshots extracted, starting transcription...")
            except Exception as e:
                error_msg = f"Screenshot extraction failed: {str(e)}"
                error_messages.append(error_msg)
                update_video_progress(job_id, 20, "error", error_msg)
                return
            
            # Transcribe audio with Whisper
            update_video_progress(job_id, 40, "transcribing", "Transcribing audio with Whisper...")
            transcript_dir = os.path.join("transcripts", job_id)
            transcript_txt = os.path.join(transcript_dir, "transcript.txt")
            try:
                from transcribe_whisper import transcribe_audio_whisper
                os.makedirs(transcript_dir, exist_ok=True)
                result = transcribe_audio_whisper(file_location, transcript_txt)
                update_video_progress(job_id, 60, "aligning", "Transcription complete, aligning with frames...")
            except Exception as e:
                error_msg = f"Whisper transcription failed: {str(e)}"
                error_messages.append(error_msg)
                update_video_progress(job_id, 40, "error", error_msg)
                return
            
            # Align subtitles with frames (optional step)
            update_video_progress(job_id, 60, "aligning", "Aligning subtitles with frames...")
            alignment_path = None
            try:
                # Look for SRT file and align with screenshots
                srt_path = os.path.splitext(transcript_txt)[0] + ".srt"
                if os.path.exists(srt_path) and os.path.exists(screenshots_dir):
                    alignment_path = os.path.join(screenshots_dir, "frame_subtitle_alignment.json")
                    # This step is optional - skip if alignment script doesn't exist
                    pass
                update_video_progress(job_id, 80, "generating", "Generating comprehensive notes...")
            except Exception as e:
                # Alignment is optional, continue without it
                print(f"Subtitle alignment skipped: {str(e)}")
                update_video_progress(job_id, 80, "generating", "Generating comprehensive notes...")
            
            # Generate notes with Gemini
            update_video_progress(job_id, 80, "generating", "Generating notes with AI...")
            notes_dir = os.path.join("notes", job_id)
            notes_md = os.path.join(notes_dir, "notes.md")
            try:
                from generate_notes_gemini import generate_notes_from_transcript
                os.makedirs(notes_dir, exist_ok=True)
                
                # Load transcript
                with open(transcript_txt, "r", encoding="utf-8") as f:
                    transcript_content = f.read()
                
                # Generate notes
                notes_content = generate_notes_from_transcript(transcript_content, alignment_path, screenshots_dir)
                
                # Save notes
                with open(notes_md, "w", encoding="utf-8") as f:
                    f.write(notes_content)
                
                update_video_progress(job_id, 100, "completed", "Video processing completed successfully!")
                JOBS[job_id] = JobStatus(job_id=job_id, status="completed")
                
            except Exception as e:
                error_msg = f"Note generation failed: {str(e)}"
                error_messages.append(error_msg)
                update_video_progress(job_id, 80, "error", error_msg)
                JOBS[job_id] = JobStatus(job_id=job_id, status="failed")
                return
                
        except Exception as e:
            error_msg = f"Video processing failed: {str(e)}"
            update_video_progress(job_id, 0, "error", error_msg)
            JOBS[job_id] = JobStatus(job_id=job_id, status="failed")
    
    # Start processing in background
    thread = threading.Thread(target=process_video)
    thread.daemon = True
    thread.start()
    
    return {"job_id": job_id}

@router.get("/video/job_status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
