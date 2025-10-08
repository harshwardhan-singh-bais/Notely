#!/usr/bin/env python3
"""
Notely Setup Verification Script
Run this after cloning the repository to verify everything is working correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is too old. Please use Python 3.8 or newer.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'python-multipart',
        'whisper', 'torch', 'cv2', 'PIL', 'yt_dlp', 
        'google.generativeai', 'clip'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                import PIL
            elif package == 'google.generativeai':
                import google.generativeai
            elif package == 'python-multipart':
                import multipart
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    print("\n🎬 Checking FFmpeg...")
    
    # Check if ffmpeg.exe exists locally
    if Path("ffmpeg.exe").exists():
        print("✅ FFmpeg found locally (ffmpeg.exe)")
        return True
    
    # Check if ffmpeg is in PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg found in PATH")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFmpeg not found")
    print("Run: python install_ffmpeg.py")
    return False

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directory structure...")
    
    required_dirs = [
        'ai_screenshots', 'transcripts', 'notes', 
        'uploaded_videos', 'uploaded_documents', 'extracted_text'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"⚠️ {dir_name}/ - Creating...")
            dir_path.mkdir(exist_ok=True)
            print(f"✅ {dir_name}/ - Created")
    
    return True

def check_env_file():
    """Check environment configuration"""
    print("\n🔑 Checking environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️ .env file not found")
            print("💡 Copy .env.example to .env and add your API keys:")
            print("   - GEMINI_API_KEY (for AI note generation)")
            print("   - OPENAI_API_KEY (optional)")
            return False
        else:
            print("❌ No .env.example file found")
            return False
    
    print("✅ .env file exists")
    
    # Check for required API keys
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if gemini_key:
            print("✅ Gemini API key configured")
        else:
            print("⚠️ Gemini API key not found - AI note generation may not work")
            print("   Add GEMINI_API_KEY to your .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed - cannot check API keys")
    
    return True

def test_basic_functionality():
    """Test basic imports and functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test FastAPI import
        from fastapi import FastAPI
        print("✅ FastAPI import")
        
        # Test video processing imports
        from extract_diagram_frames import extract_relevant_frames
        print("✅ AI screenshot extraction")
        
        from transcribe_whisper import transcribe_audio_whisper
        print("✅ Whisper transcription")
        
        from generate_notes_gemini import generate_notes_from_transcript
        print("✅ Gemini note generation")
        
        print("✅ All core functionality imports successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🚀 Notely Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("Directories", check_directories),
        ("Environment", check_env_file),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Setup Verification Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Everything looks good! You can start the application:")
        print("   Backend: uvicorn main:app --reload --port 8000")
        print("   Frontend: npm run dev (in frontend directory)")
        return True
    else:
        print("⚠️ Some issues need to be resolved before running the application.")
        print("📚 See the messages above for specific steps to fix each issue.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)