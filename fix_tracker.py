import re

with open('docs/roadmap/KNOWLEDGE_TRACKER.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('| pi-gateway |', '| pi-gateway |')
# Also fix any missing backticks
text = text.replace('pi-gateway', 'pi-gateway')

with open('docs/roadmap/KNOWLEDGE_TRACKER.md', 'w', encoding='utf-8') as f:
    f.write(text)
