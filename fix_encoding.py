import os

def fix_file(path):
    print(f"Fixing {path}...")
    try:
        # First try to read as utf-8
        with open(path, 'rb') as f:
            content = f.read()
        
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # If it fails, decode as cp1252, which is what Set-Content does by default
            text = content.decode('cp1252')
            
        # Clean control characters
        text = text.replace('\x00', '')
        text = text.replace('\x0b', '')
        text = text.replace('\x07', '')
        
        # Write back as clean UTF-8
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
            
    except Exception as e:
        print(f"Error fixing {path}: {e}")

files_to_fix = [
    'docs/DOCUMENTATION_CONSISTENCY_AUDIT.md',
    'docs/JWT_COMPARISON.md',
    'docs/architecture/CURRENT_ARCHITECTURE.md',
    'docs/exam/KNOWLEDGE_READINESS_AUDIT.md',
    'docs/roadmap/KNOWLEDGE_TRACKER.md',
    'README.md'
]

for file in files_to_fix:
    fix_file(file)

