# Changelog

## 1.1.0 — 2026-09-15

### Added

- Added an author-grouped library layout: all works by the same author are stored directly inside one author folder.
- Added a reviewed migration workflow for existing libraries: inventory first, show the proposed directory tree, wait for approval, detect conflicts, move files, and verify counts.
- Added collision-safe cover naming with `<书名> cover.jpg`.
- Added safeguards that preserve `.obsidian` and unrelated files while removing only successfully emptied legacy work folders.

### Changed

- Changed the default library location to the iCloud Obsidian vault at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/熵减/同人/`.
- Replaced the former `<作者> - <书名>/` work-folder layout with a flat `<作者>/` layout.
- Updated verification rules and UI metadata for the new organization model.

## 1.0.0 — 2026-09-08

- Initial review-first Quotev archive workflow.
- Added Markdown and cover review before TXT and EPUB publication.
- Added deterministic EPUB 2.0 generation and validation.
