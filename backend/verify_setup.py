#!/usr/bin/env python3
"""
Quick verification that all screenshot fixes are properly applied.
"""

import os

def verify_screenshot_setup():
    """Verify that the screenshot system is properly configured"""
    
    print("🎯 Screenshot System Verification")
    print("=" * 50)
    
    # Check 1: Static files exist
    job_id = "f3d4a77a-d13a-43f3-9020-f822615155ac"
    screenshot_dir = f"ai_screenshots/{job_id}"
    
    if os.path.exists(screenshot_dir):
        screenshot_count = len([f for f in os.listdir(screenshot_dir) if f.endswith('.jpg')])
        print(f"✅ Screenshot directory exists: {screenshot_dir}")
        print(f"   📸 Found {screenshot_count:,} screenshot files")
    else:
        print(f"❌ Screenshot directory missing: {screenshot_dir}")
        return False
    
    # Check 2: Backend configuration
    main_py_path = "main.py"
    if os.path.exists(main_py_path):
        with open(main_py_path, 'r') as f:
            content = f.read()
            if 'StaticFiles' in content and '/ai_screenshots' in content:
                print("✅ Backend configured with static file serving")
            else:
                print("❌ Backend missing static file configuration")
                return False
    else:
        print("❌ main.py not found")
        return False
    
    # Check 3: Notes have correct URLs
    notes_path = f"notes/{job_id}/notes.md"
    if os.path.exists(notes_path):
        with open(notes_path, 'r', encoding='utf-8') as f:
            content = f.read()
            http_urls = content.count('http://localhost:8000/ai_screenshots/')
            relative_paths = content.count('ai_screenshots/') - http_urls
            
            print(f"✅ Notes file exists: {notes_path}")
            print(f"   🌐 HTTP screenshot URLs: {http_urls}")
            print(f"   📁 Relative paths (should be 0): {relative_paths}")
            
            if http_urls > 0 and relative_paths == 0:
                print("✅ All screenshot URLs use correct HTTP format")
            else:
                print("❌ Notes contain incorrect screenshot paths")
                return False
    else:
        print(f"❌ Notes file not found: {notes_path}")
        return False
    
    # Check 4: Sample screenshot URL format
    sample_url = f"http://localhost:8000/ai_screenshots/{job_id}/frame_000900_t15.0s.jpg"
    print(f"\n📋 Sample screenshot URL format:")
    print(f"   {sample_url}")
    
    print(f"\n🎉 VERIFICATION COMPLETE!")
    print("=" * 50)
    print("✅ Static files exist")
    print("✅ Backend configured for serving")
    print("✅ Notes use HTTP URLs")
    print("✅ All components ready")
    print()
    print("🚀 TO TEST:")
    print("1. Start backend: uvicorn main:app --reload --port 8000")
    print("2. Visit: http://localhost:8000/ai_screenshots/f3d4a77a-d13a-43f3-9020-f822615155ac/frame_000900_t15.0s.jpg")
    print("3. Open frontend and view the notes - screenshots should display properly!")
    print()
    print("💡 The 'small box placeholder' issue should now be resolved!")
    
    return True

if __name__ == "__main__":
    verify_screenshot_setup()