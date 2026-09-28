import re

with open('docs/exam/KNOWLEDGE_READINESS_AUDIT.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Sessions 1"24', 'Sessions 1-24')
text = text.replace('## 1. Codebase Implementation Status: COMPLETE\\nThe repository implementation is formally complete through the boundary of Session 23 (Lab 19), with the Session 24 Architecture Wrap-Up documented in docs/architecture/clinic-2.md. \\n', '## 1. Codebase Implementation Status: MOSTLY COMPLETE\\nThe repository implementation is complete through the boundary of Session 23 (Lab 19) based on the AI-driven reconstruction of the reference material. However, not every feature is fully production-ready.\\n\\n**Known Carry-Over Gaps:**\\n- inventory-service still using ConcurrentHashMap\\n- Incomplete API versioning\\n- Missing Kafka DLQ where applicable\\n- Other technical debt explicitly documented in clinic-2.md\\n\\n')

with open('docs/exam/KNOWLEDGE_READINESS_AUDIT.md', 'w', encoding='utf-8') as f:
    f.write(text)
