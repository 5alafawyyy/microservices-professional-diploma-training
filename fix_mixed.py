import os

def fix_mixed_encoding(path):
    print(f"Fixing {path}...")
    try:
        with open(path, 'rb') as f:
            content = f.read()
            
        # Replace common Windows-1252 bytes in the raw bytes BEFORE decoding as utf-8
        # \x96 is en-dash, \x97 is em-dash, \x91 \x92 are quotes, \x93 \x94 are double quotes
        content = content.replace(b'\x96', '-'.encode('utf-8'))
        content = content.replace(b'\x97', '\u2014'.encode('utf-8')) # em-dash
        content = content.replace(b'\x91', "'".encode('utf-8'))
        content = content.replace(b'\x92', "'".encode('utf-8'))
        content = content.replace(b'\x93', '"'.encode('utf-8'))
        content = content.replace(b'\x94', '"'.encode('utf-8'))
        
        # Now decode as utf-8 with replacement for any other garbage
        text = content.decode('utf-8', errors='replace')
        
        # Clean control characters
        text = text.replace('\x00', '')
        text = text.replace('\x0b', '')
        text = text.replace('\x07', '')
        text = text.replace('\ufffd', '') # Remove replacement characters
        
        # Write back as clean UTF-8
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
            
    except Exception as e:
        print(f"Error fixing {path}: {e}")

fix_mixed_encoding('README.md')
fix_mixed_encoding('docs/architecture/CURRENT_ARCHITECTURE.md')
fix_mixed_encoding('docs/exam/KNOWLEDGE_READINESS_AUDIT.md')
