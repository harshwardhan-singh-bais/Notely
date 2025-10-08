# Notely Backend

## Setup Instructions

### Prerequisites
1. Python 3.8+
2. FFmpeg (required for video processing)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   
   **Option 1: Automatic installation (Windows)**
   ```bash
   python install_ffmpeg.py
   ```
   
   **Option 2: Manual installation**
   - Download from: https://www.gyan.dev/ffmpeg/builds/
   - Extract and add to PATH
   
   **Option 3: Using package managers**
   ```bash
   # Windows (with winget)
   winget install Gyan.FFmpeg
   
   # macOS (with Homebrew)
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## Features

- **Document Processing**: Upload and process PDF/DOCX files
- **Enhanced Video Processing**: 
  - YouTube URL support with yt-dlp
  - **NEW: Smart Subtitle Extraction** - Prioritizes accurate YouTube subtitles over audio transcription
  - Local video file upload
  - AI-powered screenshot extraction using CLIP
  - Hybrid transcription: Subtitles → Auto-captions → Whisper audio fallback
  - Enhanced note generation with transcript source metadata
- **Real-time Progress Tracking**: 0-100% progress updates
- **Notes Management**: Generated notes storage and retrieval

## Video Processing Enhancement 🆕

The video processing pipeline now uses a **smart hybrid approach**:

### Transcription Priority (for YouTube videos):
1. **🎯 Manual Subtitles** (Highest accuracy) - Uses human-created captions
2. **🔄 Auto-generated Subtitles** (Good accuracy) - Uses YouTube's auto-captions  
3. **🎵 Whisper Audio Transcription** (Fallback) - AI audio transcription

### Benefits:
- **Higher Accuracy**: Manual subtitles are more accurate than audio transcription
- **Better Performance**: Subtitle extraction is faster than audio processing
- **Enhanced Metadata**: Notes include transcript source and language information
- **Robust Fallback**: Always works even without subtitles

### Note Generation Enhancement:
Generated notes now include:
- **Transcript Source**: Manual/Auto subtitles or Whisper audio
- **Language Information**: Detected subtitle language
- **Accuracy Indicators**: Method used for transcription
- **Timing Metadata**: Subtitle timing information

## API Endpoints

### Document Processing
- `POST /document/upload/` - Upload document
- `GET /document/progress/{doc_id}` - Get processing progress
- `GET /document/list/` - List documents

### Video Processing  
- `POST /video/submit_job/` - Submit video for processing
- `GET /video/progress/{job_id}` - Get processing progress
- `GET /video/notes/{job_id}` - Get generated notes

### Notes
- `GET /notes/` - List all notes
- `GET /notes/{note_id}` - Get specific note

## Directory Structure

```
backend/
├── ai_screenshots/     # AI-extracted video screenshots
├── transcripts/        # Whisper transcriptions  
├── notes/             # Generated notes
├── uploaded_videos/   # Uploaded video files
├── uploaded_documents/ # Uploaded document files
├── extracted_text/    # Extracted document text
└── ...
```

## Environment Variables

Required in `.env` file:
- `GEMINI_API_KEY` - Google Gemini API key for note generation
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI models)
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Application secret key