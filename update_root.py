import re

with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific docs/labs/ line in the Repository Layout
old_line = "│   ├── labs/                  # Complete practical lab documentation (Official & Reconstructed)"
new_line = "│   ├── labs/                  # Complete practical lab documentation containing both official source-derived and reconstructed training labs."
text = text.replace(old_line, new_line)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated root README.md")
