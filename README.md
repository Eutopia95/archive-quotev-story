# archive-quotev-story

Personal Codex skill for archiving complete Quotev fiction into an author-grouped Chinese library with a review-first workflow. It can also reorganize an existing library after presenting a complete dry-run tree for approval.

The review phase creates Markdown and a cover. TXT and EPUB are generated only after explicit approval.

## Install with Codex

Ask Codex on the new device:

```text
Use $skill-installer to install this skill from:
https://github.com/Eutopia95/archive-quotev-story
```

If the skill does not appear after installation, restart Codex.

## Manual installation

```bash
git clone https://github.com/Eutopia95/archive-quotev-story.git ~/Documents/archive-quotev-story
mkdir -p ~/.agents/skills
ln -s ~/Documents/archive-quotev-story ~/.agents/skills/archive-quotev-story
```

Codex supports symlinked skill folders. The skill writes archived works to:

```text
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/熵减/同人/<作者>/
```

Work files are stored directly in each author folder. Covers are named `<书名> cover.jpg`; no per-work subfolder is created.

## Update

```bash
cd ~/Documents/archive-quotev-story
git pull
```

The repository contains only the skill instructions and deterministic build script. It does not contain archived fiction, covers, TXT files, or EPUB files.

See [CHANGELOG.md](CHANGELOG.md) for feature history.
