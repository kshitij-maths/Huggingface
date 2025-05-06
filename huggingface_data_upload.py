import os
import requests
import numpy as np
import time
from huggingface_hub import HfApi, HfFolder, Repository
from io import BytesIO



# Step 1: Hugging Face Authentication
hf_token = "your-token" #Replace with your token
HfFolder.save_token(hf_token)
api = HfApi()

# Step 2: Create main repository
repo_name = "Datasets"
username = "username"  # Replace with your username
full_repo_name = f"{username}/{repo_name}"
repo_url = api.create_repo(repo_id=full_repo_name, repo_type="dataset", exist_ok=True)

# Step 3: GitHub repository info
github_repo_url = "https://api.github.com/repos/mathLab/Smithers/contents/smithers/dataset/datasets"

# Step 4: Process folders and files
response = requests.get(github_repo_url)
response.raise_for_status()

for folder in response.json():
    if folder['type'] != 'dir':
        continue

    folder_name = folder['name']
    folder_content = requests.get(folder['url']).json()

    for file in folder_content:
        if file['type'] != 'file' or not file['name'].endswith('.npy'):
            continue

        try:
            # Download file content
            file_content = requests.get(file['download_url']).content
            
            # Create repository path
            repo_path = f"{folder_name}/{file['name']}"
            
            # Upload to Hugging Face Hub
            api.upload_file(
                path_or_fileobj=BytesIO(file_content),
                path_in_repo=repo_path,
                repo_id=full_repo_name,
                repo_type="dataset"
            )
            
            print(f"✅ Uploaded {repo_path}")
            time.sleep(15)  # Rate limit protection

        except Exception as e:
            print(f"❌ Failed to process {folder_name}/{file['name']}: {str(e)}")
            if "429" in str(e):
                print("⚠️ Rate limited - waiting 60 seconds")
                time.sleep(60)