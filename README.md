# archive-quotev-story

Personal Codex skill for archiving complete Quotev fiction into a Chinese library with a review-first workflow.

The review phase creates Markdown and `cover.jpg`. TXT and EPUB are generated only after explicit approval.

## Install with Codex

Ask Codex on the new device:

```text
Use $skill-installer to install this skill from:
https://github.com/Eutopia95/archive-quotev-story
```

If the skill does not appear after installation, restart Codex.

## Manual installation

Clone the repository and link it into the personal skills directory:

```bash
git clone https://github.com/Eutopia95/archive-quotev-story.git ~/Documents/archive-quotev-story
mkdir -p ~/.agents/skills
ln -s ~/Documents/archive-quotev-story ~/.agents/skills/archive-quotev-story
```

Codex supports symlinked skill folders. The skill writes archived works to:

```text
~/Downloads/同人文/<作者> - <书名>/
```

## Update

```bash
cd ~/Documents/archive-quotev-story
git pull
```

The repository contains only the skill instructions and deterministic build script. It does not contain archived fiction, covers, TXT files, or EPUB files.
