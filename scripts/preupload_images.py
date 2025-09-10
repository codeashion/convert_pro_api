#!/usr/bin/env python3
"""
Script to pre-upload images using the global upload API
"""

import requests
import os
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api"
IMAGES_TO_UPLOAD = {
    "task_icons": [
        "path/to/your/custom-icon1.png",
        "path/to/your/custom-icon2.png"
    ],
    "profile_images": [
        "path/to/your/default-avatar.png"
    ]
}

def upload_image(file_path: str, category: str, token: str = None):
    """Upload a single image file"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/png')}
            data = {'category': category}
            
            headers = {}
            if token:
                headers['token'] = token
            
            # Use task-icon endpoint for task icons (no auth required)
            if category == "task_icons":
                response = requests.post(f"{API_BASE}/upload/task-icon", files=files)
            else:
                response = requests.post(f"{API_BASE}/upload/", files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Uploaded {file_path} -> {result['file_url']}")
                return result
            else:
                print(f"❌ Failed to upload {file_path}: {response.text}")
                return None
    
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {str(e)}")
        return None

def main():
    """Main upload script"""
    print("🚀 Starting pre-upload process...")
    
    # Get auth token if needed (replace with actual login)
    # token = get_auth_token()  # Implement this if you need authentication
    token = None
    
    for category, file_paths in IMAGES_TO_UPLOAD.items():
        print(f"\n📁 Uploading {category} files...")
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                upload_image(file_path, category, token)
            else:
                print(f"❌ File not found: {file_path}")
    
    print("\n✅ Pre-upload process completed!")

if __name__ == "__main__":
    main()