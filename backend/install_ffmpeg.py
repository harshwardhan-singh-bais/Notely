"""
FFmpeg installer for Windows
"""
import os
import zipfile
import urllib.request
import sys
from pathlib import Path

def download_ffmpeg():
    """Download and install FFmpeg for Windows"""
    
    # FFmpeg download URL (essentials build)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    print("🔽 Downloading FFmpeg...")
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    zip_path = downloads_dir / "ffmpeg.zip"
    
    try:
        # Download FFmpeg
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("✅ Download complete!")
        
        # Extract FFmpeg
        print("📦 Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(downloads_dir)
        
        # Find the extracted directory
        for item in downloads_dir.iterdir():
            if item.is_dir() and "ffmpeg" in item.name.lower():
                ffmpeg_dir = item
                break
        else:
            raise Exception("Could not find extracted FFmpeg directory")
        
        # Copy ffmpeg.exe to current directory
        ffmpeg_exe = ffmpeg_dir / "bin" / "ffmpeg.exe"
        if ffmpeg_exe.exists():
            local_ffmpeg = Path("ffmpeg.exe")
            import shutil
            shutil.copy2(ffmpeg_exe, local_ffmpeg)
            print(f"✅ FFmpeg installed to: {local_ffmpeg.absolute()}")
            
            # Test if it works
            result = os.system("ffmpeg.exe -version")
            if result == 0:
                print("🎉 FFmpeg is working!")
                return True
            else:
                print("❌ FFmpeg test failed")
                return False
        else:
            print("❌ ffmpeg.exe not found in extracted files")
            return False
            
    except Exception as e:
        print(f"❌ Error installing FFmpeg: {e}")
        return False
    finally:
        # Cleanup
        if zip_path.exists():
            zip_path.unlink()

if __name__ == "__main__":
    success = download_ffmpeg()
    if success:
        print("\n🎬 FFmpeg is ready! You can now use Whisper for video transcription.")
    else:
        print("\n❌ FFmpeg installation failed. Please install manually:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract and add to PATH")
    
    sys.exit(0 if success else 1)