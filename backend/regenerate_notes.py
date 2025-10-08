#!/usr/bin/env python3
"""
Script to regenerate notes with correct time-synchronized screenshots.
"""

import os
import json

def regenerate_notes_for_job(job_id):
    """Regenerate notes for a specific job with time-synchronized screenshots"""
    
    # Paths
    transcript_dir = os.path.join("transcripts", job_id)
    transcript_txt = os.path.join(transcript_dir, "transcript.txt")
    screenshots_dir = os.path.join("ai_screenshots", job_id)
    notes_dir = os.path.join("notes", job_id)
    notes_md = os.path.join(notes_dir, "notes.md")
    
    # Check if necessary files exist
    if not os.path.exists(transcript_txt):
        print(f"❌ Transcript not found: {transcript_txt}")
        return False
    
    if not os.path.exists(screenshots_dir):
        print(f"❌ Screenshots directory not found: {screenshots_dir}")
        return False
    
    # Load transcript
    try:
        with open(transcript_txt, "r", encoding="utf-8") as f:
            transcript_content = f.read()
        print(f"✅ Loaded transcript: {len(transcript_content)} characters")
    except Exception as e:
        print(f"❌ Error loading transcript: {e}")
        return False
    
    # Import and use the note generation function
    try:
        from generate_notes_gemini import generate_notes_from_transcript
        
        print(f"🔄 Regenerating notes with time-synchronized screenshots...")
        print(f"   📁 Screenshots: {screenshots_dir}")
        print(f"   📝 Job ID: {job_id}")
        
        # Generate notes
        notes_content = generate_notes_from_transcript(
            transcript_content, 
            None,  # alignment_path
            screenshots_dir,
            "whisper_audio",  # transcript_source
            None  # subtitle_info
        )
        
        # Create output directory
        os.makedirs(notes_dir, exist_ok=True)
        
        # Save notes with metadata header
        notes_with_metadata = f"""# Video Notes

**Job ID**: {job_id}
**Transcript Method**: Whisper Audio
**Screenshots**: Time-synchronized integration

---

{notes_content}
"""
        
        with open(notes_md, "w", encoding="utf-8") as f:
            f.write(notes_with_metadata)
        
        print(f"✅ Notes regenerated successfully!")
        print(f"   📄 Saved to: {notes_md}")
        print(f"   📏 Length: {len(notes_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating notes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Regenerate for the specific job
    job_id = "f3d4a77a-d13a-43f3-9020-f822615155ac"
    
    print(f"🎯 Regenerating notes for job: {job_id}")
    print("=" * 60)
    
    success = regenerate_notes_for_job(job_id)
    
    if success:
        print("\n🎉 Notes regeneration completed successfully!")
        print("\n📋 Expected improvements:")
        print("   ✅ Correct screenshot paths (ai_screenshots/{job_id}/...)")
        print("   ✅ Time-synchronized placement")
        print("   ✅ Natural content flow")
        print("   ✅ No more broken image placeholders")
    else:
        print("\n❌ Notes regeneration failed!")