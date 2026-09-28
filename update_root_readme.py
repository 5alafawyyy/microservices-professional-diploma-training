import re

with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific docs/labs/ line in the Repository Layout
old_line = "│   ├── labs/                  # Frozen historical source lab documents (Labs 1-6A)"
new_line = "│   ├── labs/                  # Complete practical lab documentation (Official & Reconstructed)"
text = text.replace(old_line, new_line)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated root README.md")
