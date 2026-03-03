import os
import sys

try:
    from huggingface_hub import hf_hub_download
    repo_id = "Systran/faster-whisper-medium"
    
    files = [
        "config.json",
        "model.bin",
        "preprocessor_config.json",
        "tokenizer.json",
        "vocabulary.json"
    ]
    
    print(f"Downloading {len(files)} files for {repo_id}...")
    
    for file in files:
        print(f"Downloading {file}...")
        path = hf_hub_download(
            repo_id=repo_id, 
            filename=file,
            resume_download=True,
            local_files_only=False
        )
        print(f"-> Success: {path}")

    print("\nALL FILES DOWNLOADED SUCCESSFULLY!")

except Exception as e:
    print(f"\n[ERROR] Download Failed: {e}")
    sys.exit(1)
