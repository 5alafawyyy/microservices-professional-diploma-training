import os

files_to_check = [
    'README.md',
    'docs/roadmap/KNOWLEDGE_TRACKER.md',
    'docs/roadmap/MASTER_ROADMAP.md',
    'docs/roadmap/EXAM_PREPARATION_ROADMAP.md',
    'docs/roadmap/SESSION_TO_LAB_MAP.md',
    'docs/exam/KNOWLEDGE_READINESS_AUDIT.md',
    'docs/exam/REMOTE_REPOSITORY_SYNC_AUDIT.md',
    'docs/exam/REPOSITORY_ENCODING_AUDIT.md',
    'docs/REPOSITORY_STRUCTURE_AUDIT.md',
    'docs/DOCUMENTATION_CONSISTENCY_AUDIT.md',
    'docs/architecture/clinic-2.md'
]

all_clean = True

for path in files_to_check:
    if not os.path.exists(path):
        continue
    with open(path, 'rb') as f:
        content = f.read()
    
    # scan for raw bytes
    for i, b in enumerate(content):
        if b < 32 and b not in (9, 10, 13):
            print(f"FAIL: Local byte scan found control char {b} in {path} at {i}")
            all_clean = False
        if b == 0x7f:
            print(f"FAIL: Local byte scan found DEL char in {path} at {i}")
            all_clean = False
            
    try:
        text = content.decode('utf-8')
        if '\ufffd' in text:
            print(f"FAIL: Local UTF-8 scan found U+FFFD in {path}")
            all_clean = False
    except UnicodeDecodeError:
        print(f"FAIL: Local UTF-8 scan failed to decode {path}")
        all_clean = False

if all_clean:
    print("Local scan: PASS")
