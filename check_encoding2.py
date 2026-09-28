import os

def check_file(path):
    try:
        with open(path, 'rb') as f:
            content = f.read()
            
        control_chars = False
        if b'\x00' in content or b'\x07' in content or b'\x0b' in content:
            control_chars = True
            
        try:
            text = content.decode('utf-8')
            mojibake = False
            replacement = False
            
            if '' in text:
                replacement = True
            if 'â€”' in text or 'â€' in text:
                mojibake = True
                
            if control_chars:
                print(f"CORRUPTED (Control chars): {path}")
            elif replacement:
                print(f"CORRUPTED (Replacement char): {path}")
            elif mojibake:
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
