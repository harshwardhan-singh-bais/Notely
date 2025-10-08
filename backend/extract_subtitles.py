"""
Subtitle extraction utility for YouTube videos and other video sources.
Extracts subtitles/captions using yt-dlp and processes them for note generation.
"""

import os
import json
import re
from pathlib import Path
import yt_dlp


def extract_youtube_subtitles(url, output_dir):
    """
    Extract subtitles from YouTube video URL.
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save subtitle files
        
    Returns:
        dict: {
            'success': bool,
            'subtitle_file': str or None,
            'language': str or None,
            'method': str,  # 'auto' or 'manual'
            'error': str or None
        }
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure yt-dlp options for subtitle extraction
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,  # Also get auto-generated subs
        'subtitleslangs': ['en', 'en-US', 'en-GB'],  # Prefer English
        'subtitlesformat': 'vtt',  # WebVTT format is easier to parse
        'skip_download': True,  # Only download subtitles, not video
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            
            # Clean title for filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)[:50]
            
            # Check available subtitles
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            subtitle_file = None
            language = None
            method = None
            
            # Priority: Manual subtitles first, then auto-generated
            for lang_priority in ['en', 'en-US', 'en-GB']:
                # Check manual subtitles first
                if lang_priority in subtitles:
                    ydl_opts['outtmpl'] = os.path.join(output_dir, f'{safe_title}.{lang_priority}.%(ext)s')
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                        ydl_download.download([url])
                    
                    subtitle_file = os.path.join(output_dir, f'{safe_title}.{lang_priority}.vtt')
                    language = lang_priority
                    method = 'manual'
                    break
                
                # Check auto-generated subtitles
                elif lang_priority in automatic_captions:
                    ydl_opts['writesubtitles'] = False  # Only auto subs
                    ydl_opts['outtmpl'] = os.path.join(output_dir, f'{safe_title}.{lang_priority}.%(ext)s')
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                        ydl_download.download([url])
                    
                    subtitle_file = os.path.join(output_dir, f'{safe_title}.{lang_priority}.vtt')
                    language = lang_priority
                    method = 'auto'
                    break
            
            if subtitle_file and os.path.exists(subtitle_file):
                return {
                    'success': True,
                    'subtitle_file': subtitle_file,
                    'language': language,
                    'method': method,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'subtitle_file': None,
                    'language': None,
                    'method': None,
                    'error': 'No subtitles available for this video'
                }
                
    except Exception as e:
        return {
            'success': False,
            'subtitle_file': None,
            'language': None,
            'method': None,
            'error': f"Failed to extract subtitles: {str(e)}"
        }


def parse_vtt_subtitles(vtt_file):
    """
    Parse VTT subtitle file and extract clean text.
    
    Args:
        vtt_file (str): Path to VTT subtitle file
        
    Returns:
        dict: {
            'success': bool,
            'text': str,  # Clean subtitle text
            'timestamps': list,  # List of {'start': float, 'end': float, 'text': str}
            'error': str or None
        }
    """
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks
        chunks = content.split('\n\n')
        
        subtitle_text = []
        timestamps = []
        
        for chunk in chunks:
            lines = chunk.strip().split('\n')
            
            # Skip header and empty chunks
            if len(lines) < 2 or 'WEBVTT' in lines[0]:
                continue
            
            # Look for timestamp line (contains -->)
            timestamp_line = None
            text_lines = []
            
            for line in lines:
                if '-->' in line:
                    timestamp_line = line
                elif line.strip() and not line.startswith('NOTE'):
                    # Clean HTML tags and special characters
                    clean_line = re.sub(r'<[^>]+>', '', line)
                    clean_line = re.sub(r'&[a-z]+;', '', clean_line)
                    clean_line = clean_line.strip()
                    if clean_line:
                        text_lines.append(clean_line)
            
            if timestamp_line and text_lines:
                # Parse timestamp
                try:
                    time_parts = timestamp_line.split(' --> ')
                    start_time = parse_vtt_timestamp(time_parts[0].strip())
                    end_time = parse_vtt_timestamp(time_parts[1].strip())
                    
                    text = ' '.join(text_lines)
                    subtitle_text.append(text)
                    timestamps.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
                except:
                    continue
        
        # Join all subtitle text
        full_text = ' '.join(subtitle_text)
        
        return {
            'success': True,
            'text': full_text,
            'timestamps': timestamps,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'timestamps': [],
            'error': f"Failed to parse VTT file: {str(e)}"
        }


def parse_vtt_timestamp(timestamp_str):
    """
    Parse VTT timestamp format to seconds.
    Format: HH:MM:SS.mmm or MM:SS.mmm
    """
    try:
        # Remove any extra characters
        timestamp_str = timestamp_str.split()[0]
        
        # Split by colons
        parts = timestamp_str.split(':')
        
        if len(parts) == 3:  # HH:MM:SS.mmm
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS.mmm
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return 0.0
    except:
        return 0.0


def extract_and_process_subtitles(url, output_dir):
    """
    Complete pipeline: extract subtitles and process them to clean text.
    
    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save files
        
    Returns:
        dict: {
            'success': bool,
            'subtitle_text': str,  # Clean subtitle text for note generation
            'subtitle_file': str or None,
            'language': str or None,
            'method': str or None,  # 'auto' or 'manual'
            'timestamps': list,  # Timing information
            'error': str or None
        }
    """
    # Step 1: Extract subtitles
    extract_result = extract_youtube_subtitles(url, output_dir)
    
    if not extract_result['success']:
        return {
            'success': False,
            'subtitle_text': '',
            'subtitle_file': None,
            'language': None,
            'method': None,
            'timestamps': [],
            'error': extract_result['error']
        }
    
    # Step 2: Parse subtitle file
    parse_result = parse_vtt_subtitles(extract_result['subtitle_file'])
    
    if not parse_result['success']:
        return {
            'success': False,
            'subtitle_text': '',
            'subtitle_file': extract_result['subtitle_file'],
            'language': extract_result['language'],
            'method': extract_result['method'],
            'timestamps': [],
            'error': parse_result['error']
        }
    
    return {
        'success': True,
        'subtitle_text': parse_result['text'],
        'subtitle_file': extract_result['subtitle_file'],
        'language': extract_result['language'],
        'method': extract_result['method'],
        'timestamps': parse_result['timestamps'],
        'error': None
    }


if __name__ == "__main__":
    # Test the subtitle extraction
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_subtitles.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = "test_subtitles"
    
    print(f"Extracting subtitles from: {url}")
    result = extract_and_process_subtitles(url, output_dir)
    
    if result['success']:
        print(f"✅ Success!")
        print(f"Language: {result['language']}")
        print(f"Method: {result['method']}")
        print(f"Text length: {len(result['subtitle_text'])} characters")
        print(f"Timestamps: {len(result['timestamps'])} segments")
        print(f"\nFirst 500 characters:")
        print(result['subtitle_text'][:500])
    else:
        print(f"❌ Failed: {result['error']}")