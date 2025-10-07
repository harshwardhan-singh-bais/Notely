import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_api_key():
    # Try both environment variable names
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
    return api_key

def load_inputs(transcript_path, alignment_path=None, doc_text_path=None):
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    alignment = None
    if alignment_path and os.path.exists(alignment_path):
        with open(alignment_path, "r", encoding="utf-8") as f:
            alignment = json.load(f)
    doc_text = None
    if doc_text_path and os.path.exists(doc_text_path):
        with open(doc_text_path, "r", encoding="utf-8") as f:
            doc_text = f.read()
    return transcript, alignment, doc_text

def build_prompt(transcript, alignment=None, doc_text=None):
    prompt = """You are an expert note-taker. Given the following transcript and (optionally) document text and screenshot alignments, generate extensive, human-like notes. Interleave text and image references (e.g., [Image: frame_123.jpg]) where relevant. Use markdown for formatting.\n\n"""
    prompt += f"Transcript:\n{transcript}\n\n"
    if doc_text:
        prompt += f"Document Text:\n{doc_text}\n\n"
    if alignment:
        prompt += f"Frame-Subtitle Alignment (JSON):\n{json.dumps(alignment)[:2000]}...\n\n"  # Truncate for prompt size
    prompt += "Generate the notes below:\n"
    return prompt

def generate_notes_gemini(prompt, api_key, model_name="models/gemini-2.5-flash"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

def main(transcript_path, output_path, alignment_path=None, doc_text_path=None):
    api_key = load_api_key()
    transcript, alignment, doc_text = load_inputs(transcript_path, alignment_path, doc_text_path)
    prompt = build_prompt(transcript, alignment, doc_text)
    notes = generate_notes_gemini(prompt, api_key)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(notes)
    print(f"Generated notes saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python generate_notes_gemini.py <transcript_path> <output_path> [alignment_path] [doc_text_path]")
        exit(1)
    transcript_path = sys.argv[1]
    output_path = sys.argv[2]
    alignment_path = sys.argv[3] if len(sys.argv) > 3 else None
    doc_text_path = sys.argv[4] if len(sys.argv) > 4 else None
    try:
        main(transcript_path, output_path, alignment_path, doc_text_path)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
