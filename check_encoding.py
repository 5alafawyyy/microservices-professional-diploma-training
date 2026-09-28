import os
import re

def check_file(path):
    try:
        with open(path, 'rb') as f:
            content = f.read()
            
        # Check for null bytes and other control chars
        if b'\x00' in content or b'\x07' in content or b'\x0b' in content:
            print(f"CORRUPTED (Control chars): {path}")
            return
            
        try:
            text = content.decode('utf-8')
            if '' in text:
                print(f"CORRUPTED (Replacement char): {path}")
            elif 'â€”' in text or 'â€' in text:
                print(f"CORRUPTED (Mojibake): {path}")
        except UnicodeDecodeError:
            print(f"CORRUPTED (Not valid UTF-8): {path}")
            
    except Exception as e:
        print(f"Error checking {path}: {e}")

for root, _, files in os.walk('docs'):
    for file in files:
        if file.endswith(('.md', '.txt', '.yml', '.yaml', '.json')):
            check_file(os.path.join(root, file))

check_file('README.md')
