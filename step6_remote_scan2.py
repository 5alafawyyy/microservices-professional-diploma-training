import subprocess
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
    # use git show origin/main:path to get the actual remote blob
    try:
        res = subprocess.run(['git', 'show', f'origin/main:{path}'], capture_output=True, check=True)
        content = res.stdout
    except subprocess.CalledProcessError:
        print(f"FAIL: Remote file not found: {path}")
        all_clean = False
        continue

    # scan for raw bytes
    for i, b in enumerate(content):
        if b < 32 and b not in (9, 10, 13):
            print(f"FAIL: Remote byte scan found control char {b} in {path} at {i}")
            all_clean = False
        if b == 0x7f:
            print(f"FAIL: Remote byte scan found DEL char in {path} at {i}")
            all_clean = False
            
    try:
        text = content.decode('utf-8')
        if '\ufffd' in text:
            print(f"FAIL: Remote UTF-8 scan found U+FFFD in {path}")
            all_clean = False
            
        if path == 'README.md':
            expected = "Sessions 1\u201324 curriculum implementation/review completed; independent knowledge validation and capstone readiness assessment remain."
            if expected not in text:
                print(f"FAIL: Exact expected string missing in remote README.md")
                all_clean = False
                
        if path == 'docs/roadmap/KNOWLEDGE_TRACKER.md':
            # check for exact match of corrupted string
            if '| pi-gateway |' in text or 'pi-gateway' in text.replace('pi-gateway', ''):
                print(f"FAIL: 'pi-gateway' control char artifact found in remote KNOWLEDGE_TRACKER.md")
                all_clean = False
                
    except UnicodeDecodeError:
        print(f"FAIL: Remote UTF-8 scan failed to decode {path}")
        all_clean = False

if all_clean:
    print("Remote scan: PASS")
