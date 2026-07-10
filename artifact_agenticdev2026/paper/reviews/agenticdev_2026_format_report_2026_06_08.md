# AgenticDev 2026 Format Adaptation Report

Date: 2026-06-08

## Target

- Venue: AgenticDev 2026, co-located with ASE 2026.
- Track: Full Paper.
- Format: ACM `sigconf`, anonymous review.
- Limit: 10 pages of manuscript content plus up to 2 pages containing only
  references.

Official call:
https://conf.researchr.org/home/ase-2026/agenticdev-2026

## Completed

- Migrated `paper/main.tex` to
  `\documentclass[sigconf,review,anonymous,pbalance]{acmart}`.
- Added AgenticDev 2026 conference metadata, ACM CCS concepts, and keywords.
- Switched citations and bibliography to ACM numeric formatting.
- Added accessible descriptions for all four main figures.
- Added a concise Conclusion, AI-Assistance Disclosure, and final Data
  Availability Statement.
- Removed submission-stage author, funding, and competing-interest
  placeholders from the compiled manuscript.
- Compressed Limitations from eight long subsections to four focused
  subsections without strengthening empirical claims.
- Cleared unassigned DOI and ISBN metadata.
- Preserved the primary same-model and supplementary structural-control
  experiment boundary.

## Verification

- Output: `paper/main_agenticdev.pdf`.
- Page size: US Letter.
- Total pages: 11.
- Manuscript content: pages 1-10.
- References only: page 11.
- Undefined citations/references: none.
- Overfull horizontal boxes: none.
- Pages 1, 3, 6, 7, 10, and 11 were rendered and visually inspected.

## Remaining Submission Metadata

- Replace anonymous author and affiliation fields only for the camera-ready
  version or if the venue changes its anonymity instruction.
- Provide the actual anonymized artifact link at submission if available, then
  replace it with a permanent public archive in the camera-ready version.
- Recheck the official call immediately before submission for deadline or
  metadata updates.
