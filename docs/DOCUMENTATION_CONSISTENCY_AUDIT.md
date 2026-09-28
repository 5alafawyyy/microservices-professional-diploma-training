# Documentation Consistency Audit

## Duplicated READMEs
- README.md (root) vs docs/labs/README.md. The root README.md serves as the master status tracker. docs/labs/README.md was created as an index for early labs (1-5A) and stops tracking after Lab 5A. This duplication is historically accurate to the training progression and should be kept separate.

## Duplicated Roadmaps
- Various roadmaps (MASTER_ROADMAP.md, PHASE_1_ROADMAP.md, SESSION_TO_LAB_MAP.md) exist under docs/roadmap/. They serve complementary purposes rather than duplicating.

## Conflicting Completion Statuses
- The root README.md accurately lists Lab 19 (Session 23) as the last completed lab.
- docs/labs/README.md only tracks up to Lab 5A. This reflects historical state and should NOT be modified.

## Stale "Next Lab" / "Last Lab" Values
- Root README.md was updated. Last Lab is Lab 19 (Session 23). Next lab is Session 24 (Wrap-up). Correct.

## Inconsistent Lab/Session Numbering
- The curriculum exhibits inherent numbering inconsistencies:
  - Labs 1-6A map to Sessions 1-8.
  - Labs 18 and 19 map to Sessions 22 and 23.
  - Slide-only labs occupy the middle sessions.
  - This is documented in SESSION_TO_LAB_MAP.md and is a known source characteristic.

## Unicode/Encoding Corruption
- The root README.md experienced Unicode/encoding corruption (x90, x97) during script writes. A note was appended regarding cp1252 vs UTF-8.
- docs/architecture/CURRENT_ARCHITECTURE.md also contains potential encoding issues if read without explicit UTF-8 decoding.

## Official Status vs Training Artifacts
- The lab-XX nested folders in docs/labs/ are training artifacts, not original source structure. The source repo only uses flat session-XX-lab-YY.md files.

## References to Missing Files
- The root README.md references scripts/ (erify-environment.sh, erify-lab.sh, 
eset-lab.sh) which do not exist in the training repo.
- The root README.md references docs/testing/, docs/exam/, docs/setup/, etc. Some exist, some do not.

## Session 24 / Assessment Status
- The platform is structurally complete (Lab 19 finished), but Session 24 (Capstone Preparation / Wrap-up) is pending. We have not claimed completion of the final assessment yet.
