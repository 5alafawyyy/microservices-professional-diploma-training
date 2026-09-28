import os
import re

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

for path in files_to_check:
    if not os.path.exists(path):
        continue
    with open(path, 'rb') as f:
        content = f.read()
    
    # decode utf-8
    try:
        text = content.decode('utf-8')
    except Exception as e:
        text = content.decode('cp1252', errors='replace')
        
    # strip control characters except \t, \n, \r
    clean_chars = []
    fixed = False
    for char in text:
        code = ord(char)
        if code < 32 and code not in (9, 10, 13):
            fixed = True
            continue # strip
        if code == 0x7f or code == 0xfffd:
            fixed = True
            continue # strip
        clean_chars.append(char)
        
    if fixed:
        print(f"Fixed control/invalid characters in {path}")
        
    clean_text = "".join(clean_chars)
    
    # verify 'api-gateway'
    if path.endswith('KNOWLEDGE_TRACKER.md'):
        clean_text = clean_text.replace('pi-gateway', 'api-gateway')
        clean_text = clean_text.replace('aapi-gateway', 'api-gateway')
        
    # check README.md specific text
    if path == 'README.md':
        expected = "Sessions 1\u201324 curriculum implementation/review completed; independent knowledge validation and capstone readiness assessment remain."
        if expected not in clean_text:
            print("WARNING: Exact expected string missing in README.md, attempting injection")
            # Replace whatever is there with the exact string
            clean_text = re.sub(r'Sessions 1.*?remain\.', expected, clean_text, flags=re.DOTALL)
            
    with open(path, 'w', encoding='utf-8') as f:
        f.write(clean_text)

