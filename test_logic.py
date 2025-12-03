
import os
import time
from datetime import datetime

DATA_DIR = "/app/data"
TODO_DIR = os.path.join(DATA_DIR, "todo")
WORKING_DIR = os.path.join(DATA_DIR, "working")
DONE_DIR = os.path.join(DATA_DIR, "done")

# Ensure directories exist
os.makedirs(TODO_DIR, exist_ok=True)
os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)

def get_files(directory, sort_by_time=False):
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if sort_by_time:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        else:
            files.sort()
        return files
    except Exception as e:
        print(f"Error in get_files: {e}")
        return []

def get_file_choices(directory, sort_by_time=False):
    files = get_files(directory, sort_by_time)
    choices = []
    for f in files:
        path = os.path.join(directory, f)
        try:
            # Get timestamp
            mtime = os.path.getmtime(path)
            dt_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

            # Only read first 50 chars
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read(50).strip().replace('\n', ' ')
                if len(content) == 50: # approximate check
                     content += "..."

            # Format: "[YYYY-MM-DD HH:MM] filename - content..."
            label = f"[{dt_str}] {f} - {content}"
            choices.append((label, f))
        except Exception as e:
            print(f"Error processing file {f}: {e}")
            choices.append((f, f))
    return choices

print("Testing get_files(TODO_DIR)...")
print(get_files(TODO_DIR))

print("Testing get_files(WORKING_DIR)...")
print(get_files(WORKING_DIR))

print("Testing get_file_choices(DONE_DIR)...")
print(get_file_choices(DONE_DIR, sort_by_time=True))
