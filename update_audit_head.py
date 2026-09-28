import re
import subprocess

with open('docs/exam/REMOTE_REPOSITORY_SYNC_AUDIT.md', 'rb') as f:
    text = f.read().decode('utf-8')

# Get current head
res = subprocess.run(['git', 'rev-parse', 'origin/main'], capture_output=True, check=True)
current_head = res.stdout.decode('utf-8').strip()[:7]

replacement = f"""## Git Configuration & Status

- **Verification Target Commit:** 57a0ef9
- **Current Remote HEAD:** {current_head}
- **Note:** The critical repository files were verified against remote commit 57a0ef9. The resulting audit was subsequently committed. The audit commit changes only audit/documentation metadata and does not alter the verified implementation/documentation files."""

# Replace the specific section
text = re.sub(r'## Git Configuration & Status.*?## Exact Remote', replacement + '\n\n## Exact Remote', text, flags=re.DOTALL)

with open('docs/exam/REMOTE_REPOSITORY_SYNC_AUDIT.md', 'wb') as f:
    f.write(text.encode('utf-8'))
