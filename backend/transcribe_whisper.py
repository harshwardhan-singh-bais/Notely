import os
import whisper
from tqdm import tqdm

def transcribe_audio_whisper(audio_path, output_path=None, model_size="base"):
    model = whisper.load_model(model_size)
    print(f"Transcribing {audio_path} with Whisper ({model_size})...")
    result = model.transcribe(audio_path, verbose=True)
    # Save transcript as .txt and .json
    base = os.path.splitext(audio_path)[0]
    txt_path = output_path or base + "_transcript.txt"
    json_path = output_path or base + "_transcript.json"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    with open(json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Transcript saved to {txt_path} and {json_path}")
    return result

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
