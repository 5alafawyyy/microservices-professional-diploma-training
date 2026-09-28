# Repository Structure Audit

| Path | Exists? | Original/Added | Purpose | Source/Evidence | Should Keep? | Action |
|---|---|---|---|---|---|---|
| docs/ | Yes | Original | Root documentation directory | Present in reference repo | Yes | Keep |
| docs/labs/ | Yes | Original | Contains official lab documents | Present in reference repo | Yes | Keep |
| docs/labs/README.md | Yes | Added | Describes Labs 1-5A | Created in commit fc45c61 | Yes | Keep (Historical) |
| docs/labs/lab-01/ | Yes | Added | Nested lab documentation | Created in commit fc45c61 | Yes | Keep (Historical) |
| docs/labs/lab-01/README.md | Yes | Added | Reconstructed Lab 1 doc | Created in commit fc45c61 | Yes | Keep (Historical) |
| docs/labs/lab-01/acceptance.md | Yes | Added | Acceptance criteria for Lab 1 | Created in commit fc45c61 | Yes | Keep (Historical) |
| docs/labs/lab-02a/session-02-lab-02.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit 3d5d95d | Yes | Consider moving to docs/labs/ |
| docs/labs/lab-02b/session-03-lab-2b.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit b2109c9 | Yes | Consider moving to docs/labs/ |
| docs/labs/lab-03a/session-04-lab-3a.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit 1508f23 | Yes | Consider moving to docs/labs/ |
| docs/labs/lab-03b/session-05-lab-3b.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit a312230 | Yes | Consider moving to docs/labs/ |
| docs/labs/lab-04b/session-07-lab-5a.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit 928a2ab | Yes | Consider moving to docs/labs/ |
| docs/labs/lab-05a/session-08-lab-6a.md | Yes | Mixed | Official lab doc, but misplaced in subdirectory | Copied from ref repo, but nested in commit 08e02d2 | Yes | Consider moving to docs/labs/ |
| docs/lectures/ | Yes | Original | Lecture notes | Present in reference repo structure implied | Yes | Keep |
| docs/roadmap/ | Yes | Original | Master roadmaps | Present in reference repo structure implied | Yes | Keep |
| docs/architecture/ | Yes | Original | Architecture diagrams/notes | Present in reference repo | Yes | Keep |
| docs/decisions/ | Yes | Original | Architecture Decision Records | Present in reference repo structure implied | Yes | Keep |
| docs/testing/ | No | Original | Testing strategy | Missing in training repo | N/A | Note missing |
| docs/exam/ | Yes | Original | Exam prep materials | Created in early commits | Yes | Keep |
| docs/setup/ | No | Original | Setup guides | Present in reference repo, missing here | N/A | Note missing |
| docs/trainer/ | No | Original | Trainer checklists | Present in reference repo, missing here | N/A | Note missing |
| docs/grading/ | No | Original | Grading rubrics | Present in reference repo, missing here | N/A | Note missing |
| platform/ | Yes | Original | Codebase root | Present in reference repo | Yes | Keep |
| platform/ecommerce-platform/ | Yes | Original | Codebase root | Present in reference repo | Yes | Keep |
| scripts/ | No | Original | Helper scripts | Present in reference repo structure implied | N/A | Note missing |
| k6/ | Yes | Added | Load testing scripts | Copied from reference repo in Lab 19 | Yes | Keep |
| README.md | Yes | Original | Root project README | Present in reference repo (but heavily modified for training status) | Yes | Keep |
