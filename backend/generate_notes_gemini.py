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

def build_prompt(transcript, alignment=None, doc_text=None, transcript_source="unknown", subtitle_info=None, screenshot_metadata=None):
    prompt = """You are an expert note-taker. Given the following transcript and (optionally) document text, screenshot information, and alignments, generate extensive, human-like notes. 

IMPORTANT: When you reference visual content mentioned in the transcript (like diagrams, code, charts, etc.), include screenshot references using this format: ![Screenshot](relative/path/to/screenshot.jpg) or [Image: description at timestamp].

Use markdown for formatting and create comprehensive notes that integrate the transcript content with visual references.\n\n"""
    
    # Add transcript source information
    if transcript_source == "manual_subtitles":
        prompt += "**Transcript Source**: Manual subtitles/captions (high accuracy)\n\n"
    elif transcript_source == "auto_subtitles":
        prompt += "**Transcript Source**: Auto-generated subtitles (good accuracy)\n\n"
    elif transcript_source == "whisper_audio":
        prompt += "**Transcript Source**: AI audio transcription (Whisper)\n\n"
    else:
        prompt += "**Transcript Source**: Unknown\n\n"
    
    prompt += f"**Transcript Content**:\n{transcript}\n\n"
    
    # Add screenshot information if available
    if screenshot_metadata:
        prompt += f"**Available Screenshots** ({len(screenshot_metadata)} images captured):\n"
        
        # Group screenshots by content type
        content_types = {}
        for item in screenshot_metadata:
            content_type = item.get('prompt_matched', 'unknown')
            if content_type not in content_types:
                content_types[content_type] = []
            content_types[content_type].append(item)
        
        for content_type, items in content_types.items():
            prompt += f"\n**{content_type.title()}** ({len(items)} screenshots):\n"
            
            # Show first few examples with timestamps
            for i, item in enumerate(items[:5]):  # Show first 5 of each type
                timestamp = item.get('timestamp', 0)
                filename = item.get('filename', 'unknown')
                confidence = item.get('confidence', 0)
                prompt += f"- {filename} at {timestamp:.1f}s (confidence: {confidence:.2f})\n"
            
            if len(items) > 5:
                prompt += f"- ... and {len(items) - 5} more screenshots of this type\n"
        
        prompt += f"\n**Instructions for Screenshot Integration**:\n"
        prompt += f"- Reference screenshots when discussing visual content\n"
        prompt += f"- Use format: ![Description](ai_screenshots/[job_id]/filename.jpg)\n"
        prompt += f"- Include timestamps for context\n"
        prompt += f"- Group related screenshots in relevant sections\n\n"
    
    if subtitle_info:
        prompt += f"**Subtitle Information**:\n"
        prompt += f"- Language: {subtitle_info.get('language', 'Unknown')}\n"
        prompt += f"- Method: {subtitle_info.get('method', 'Unknown')}\n"
        prompt += f"- Segments: {len(subtitle_info.get('timestamps', []))}\n\n"
    
    if doc_text:
        prompt += f"**Document Text**:\n{doc_text}\n\n"
    if alignment:
        prompt += f"**Frame-Subtitle Alignment (JSON)**:\n{json.dumps(alignment)[:2000]}...\n\n"  # Truncate for prompt size
    
    prompt += """
**Generate comprehensive notes that:**
1. Summarize the main content from the transcript
2. Include screenshot references at appropriate points
3. Use proper markdown formatting
4. Create logical sections and subsections
5. Highlight key concepts and important information
6. Integrate visual content seamlessly with text

Generate the notes below:
"""
    return prompt

def generate_notes_gemini(prompt, api_key, model_name="models/gemini-2.5-flash"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

def enhance_notes_with_screenshots(notes, screenshot_metadata, screenshots_dir):
    """
    Post-process the generated notes to ensure screenshot references are properly formatted
    and add strategic screenshot placements if the AI didn't include enough
    """
    if not screenshot_metadata:
        return notes
    
    # Extract job_id from screenshots_dir path
    job_id = os.path.basename(screenshots_dir)
    
    # Add a visual content section at the end if not already present
    if "## Visual Content" not in notes and "## Screenshots" not in notes:
        notes += f"\n\n## Visual Content\n\n"
        notes += f"This video contains {len(screenshot_metadata)} captured screenshots showing:\n\n"
        
        # Group by content type for summary
        content_summary = {}
        for item in screenshot_metadata:
            content_type = item.get('prompt_matched', 'unknown')
            content_summary[content_type] = content_summary.get(content_type, 0) + 1
        
        for content_type, count in content_summary.items():
            notes += f"- **{content_type.title()}**: {count} screenshots\n"
        
        notes += f"\n### Key Screenshots\n\n"
        
        # Add a selection of high-confidence screenshots
        high_confidence_screenshots = [
            item for item in screenshot_metadata 
            if item.get('confidence', 0) > 0.7
        ]
        
        # Sort by timestamp and take every few screenshots to avoid overwhelming
        high_confidence_screenshots.sort(key=lambda x: x.get('timestamp', 0))
        selected_screenshots = high_confidence_screenshots[::max(1, len(high_confidence_screenshots) // 10)]
        
        for item in selected_screenshots[:10]:  # Limit to 10 screenshots
            timestamp = item.get('timestamp', 0)
            filename = item.get('filename', '')
            content_type = item.get('prompt_matched', 'Content')
            confidence = item.get('confidence', 0)
            
            # Convert timestamp to minutes:seconds format
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            time_str = f"{minutes}:{seconds:02d}"
            
            notes += f"**{content_type.title()} at {time_str}**\n\n"
            notes += f"![{content_type} screenshot](ai_screenshots/{job_id}/{filename})\n\n"
            notes += f"*Captured at {timestamp:.1f}s - Confidence: {confidence:.2f}*\n\n"
    
    return notes

def generate_notes_from_transcript(transcript_content, alignment_path=None, screenshots_dir=None, transcript_source="unknown", subtitle_info=None):
    """Generate notes from transcript content directly (for API calls)"""
    api_key = load_api_key()
    
    # Load alignment if available
    alignment = None
    if alignment_path and os.path.exists(alignment_path):
        with open(alignment_path, "r", encoding="utf-8") as f:
            alignment = json.load(f)
    
    # Load screenshot metadata if available
    screenshot_metadata = None
    if screenshots_dir and os.path.exists(screenshots_dir):
        metadata_file = os.path.join(screenshots_dir, "frame_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    screenshot_metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load screenshot metadata: {e}")
    
    # Build prompt with transcript content, source information, and screenshots
    prompt = build_prompt(transcript_content, alignment, None, transcript_source, subtitle_info, screenshot_metadata)
    
    # Generate notes
    notes = generate_notes_gemini(prompt, api_key)
    
    # Post-process notes to ensure screenshot references are properly formatted
    if screenshot_metadata:
        notes = enhance_notes_with_screenshots(notes, screenshot_metadata, screenshots_dir)
    
    return notes

def main(transcript_path, output_path, alignment_path=None, doc_text_path=None, transcript_source="unknown", screenshots_dir=None):
    api_key = load_api_key()
    transcript, alignment, doc_text = load_inputs(transcript_path, alignment_path, doc_text_path)
    
    # Load screenshot metadata if available
    screenshot_metadata = None
    if screenshots_dir and os.path.exists(screenshots_dir):
        metadata_file = os.path.join(screenshots_dir, "frame_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    screenshot_metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load screenshot metadata: {e}")
    
    prompt = build_prompt(transcript, alignment, doc_text, transcript_source, None, screenshot_metadata)
    notes = generate_notes_gemini(prompt, api_key)
    
    # Enhance notes with screenshots if available
    if screenshot_metadata:
        notes = enhance_notes_with_screenshots(notes, screenshot_metadata, screenshots_dir)
    
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
