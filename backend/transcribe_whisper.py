import os
import whisper
from tqdm import tqdm
import json
from pathlib import Path

def transcribe_audio_whisper(audio_path, output_path=None, model_size="base"):
    """Transcribe audio/video using Whisper with better Windows path handling"""
    try:
        # Handle problematic characters in paths
        import re
        
        # Convert to Path object for better Windows compatibility
        audio_path = Path(audio_path).resolve()
        
        # Check if file exists
        if not audio_path.exists():
            # Try to find the file with a different name pattern
            parent_dir = audio_path.parent
            filename = audio_path.name
            print(f"File not found: {audio_path}")
            print(f"Searching in directory: {parent_dir}")
            
            if parent_dir.exists():
                print("Files in directory:")
                for f in parent_dir.iterdir():
                    print(f"  - {f.name}")
                
                # Try to find a similar file
                job_id = filename.split('_')[0] if '_' in filename else None
                if job_id:
                    for f in parent_dir.iterdir():
                        if f.name.startswith(job_id) and f.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                            print(f"Found similar file: {f}")
                            audio_path = f
                            break
            
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing {audio_path} with Whisper ({model_size})...")
        print(f"File exists: {audio_path.exists()}")
        print(f"File size: {audio_path.stat().st_size} bytes")
        
        # Load Whisper model
        model = whisper.load_model(model_size)
        
        # Use raw string path for Whisper (convert Path to string with proper escaping)
        audio_path_str = str(audio_path)
        print(f"Using path for Whisper: {audio_path_str}")
        
        # Transcribe using string path (Whisper expects string, not Path)
        result = model.transcribe(audio_path_str, verbose=True)
        
        # Handle output paths
        if output_path:
            output_path = Path(output_path).resolve()
            txt_path = output_path
            json_path = output_path.with_suffix('.json')
        else:
            base_path = audio_path.with_suffix('')
            txt_path = base_path.with_suffix('.txt')
            json_path = base_path.with_suffix('.json')
        
        # Ensure output directory exists
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save transcript as .txt
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # Save detailed transcript as .json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Transcript saved to {txt_path}")
        print(f"Detailed transcript saved to {json_path}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in transcription: {e}")
        print(f"Audio path: {audio_path}")
        print(f"Audio path type: {type(audio_path)}")
        if hasattr(e, '__traceback__'):
            import traceback
            traceback.print_exc()
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python transcribe_whisper.py <audio_or_video_path> [output_path]")
        exit(1)
    audio_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        transcribe_audio_whisper(audio_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
