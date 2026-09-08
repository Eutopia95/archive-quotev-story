---
name: archive-quotev-story
description: Archive complete Quotev fiction into a personal Chinese library with a review-first workflow. Use for Quotev 小说、同人文、正文整理、封面、Markdown、TXT 或 Kindle EPUB；默认先生成可审核的 Markdown 和封面，确认后再生成 TXT 与 EPUB. Do not use for unrelated sites or a single pasted excerpt.
---

# Archive Quotev Story

Archive Quotev stories into the current user's library. Resolve `~` to the
current user's home directory before any filesystem operation:

```text
~/Downloads/同人文/<作者> - <书名>/
├── cover.jpg
├── <书名> by <作者>.md
├── <书名> by <作者>.txt       # only after approval
└── <书名> by <作者>.epub      # only after approval
```

The folder uses `作者 - 书名`; filenames and MD/TXT first lines use `书名 by 作者`.

## Choose the phase

- Default and for new links: **review phase**. Generate and install only Markdown and `cover.jpg`.
- Do not install TXT or EPUB until the user explicitly approves the reviewed Markdown, chapter titles, body cleanup, and cover.
- When the user approves: **publication phase**. Generate TXT and EPUB from the current library Markdown, not from stale extraction JSON. Preserve the reviewed headings and text exactly.
- A title, body, or cover edit during review updates only the reviewed files unless the user also asks to rebuild TXT/EPUB.

## Required tools

- Use an available Browser or Chrome skill/runtime to read rendered Quotev pages. Read its `SKILL.md` when listed. Do not substitute guessed URL ranges or ad-hoc HTTP scraping.
- Use ImageGen only when content-aware cover extension or repair is truly needed; read its `SKILL.md` first. Prefer non-generative padding when it preserves the complete original cover cleanly.
- Use `scripts/build_quotev_outputs.py` for deterministic output and EPUB validation. It may build all formats in a temporary directory during review, but install only the formats authorized for the current phase.

## Extract the complete story

1. Open the supplied work URL, explicitly navigating to chapter `/1` when a bare story URL resumes at a later chapter.
2. Read the displayed title, author, description, maturity rating, `og:image`, and visible chapter directory.
3. Discover chapters only from directory links matching the same story ID. Deduplicate exact URLs and sort by numeric URL suffix; gaps are allowed.
4. Visit every discovered chapter URL. Extract the displayed chapter title (normally `#quizSubtitle`) and only `#rescontent`.
5. Preserve source text without summarizing, rewriting, censoring, or adding prose.
6. Remove browser contamination such as a trailing `登录或注册并选择“添加到库”以关注此故事的更新`.
7. Remove one repeated heading line at a chapter opening:
   - exact duplicate of the displayed chapter title; or
   - a standalone numeric line such as `01.`, `13`, `C.1`, or `CH-13` that merely repeats the normalized chapter number, even when short author notes precede it.
   Do not remove a number used as genuine prose.
8. Preserve genuine placeholders such as `占位` and report them as source content.
9. Record embedded body images. Ignore icons, avatars, separators, and social controls.

For large works, extract in bounded batches and save every completed batch. A timeout must not discard the whole story.

## Normalize names and headings

- Prefer the user's exact work title. Otherwise remove clear category/status wrappers such as leading `博君一肖】` and terminal `（完结）`, `完结`, `丨新`, or `R/（R）`; preserve ambiguous text.
- Number chapters by actual reading order with at least two digits: `01`, `02`, …, `100`.
- Remove redundant work-name prefixes and duplicate numeric forms from headings: `13 CH-13` → `13`; `01 C.1` → `01`.
- Preserve meaningful labels: `01 引子`, `01 前章`, `28 完结`, `50 大结局`, `51 番外一`, `42 拜拜啦`, or `34 小鱼想说的！`.
- If the user manually revises a heading scheme, treat the current Markdown as authoritative for publication.
- Do not add author, URL, chapter count, or maturity bullets at the top. The first line is exactly `<书名> by <作者>`. A short source description may follow after a blank line.

## Normalize body whitespace

- Markdown and TXT paragraphs must not begin with literal spaces, tabs, ideographic spaces, or non-breaking spaces. These can turn whole paragraphs into indented blocks in Markdown readers.
- EPUB paragraph text must also have no literal leading whitespace. Apply normal first-line indentation only through CSS: `p{text-indent:2em}`.
- When repairing whitespace, compare text after leading-whitespace removal so punctuation and wording remain unchanged.

## Prepare the cover

1. Export the work's own `og:image` through page assets.
2. Save `cover.jpg` as JPEG, exactly 1080×1440 pixels (3:4), with 300-DPI metadata.
3. Preserve original art and typography. Crop only when no person, title, seal, or focal object is lost.
4. For square or landscape originals, prefer a clean, source-matched canvas extension/padding that keeps the full image. Use ImageGen only when a content-aware extension is necessary.
5. Do not add missing title text by default. For requested text edits, create non-destructive previews and wait for explicit approval before replacing the library cover or EPUB cover. Chinese spelling must be exact.

## Build data

Use UTF-8 JSON for `scripts/build_quotev_outputs.py`:

```json
{
  "title": "书名",
  "author": "作者",
  "display_title": "书名 by 作者",
  "description": ["可选简介"],
  "source_id": "Quotev story ID",
  "source_url": "canonical story URL",
  "chapters": [
    {"label": "01", "text": "正文"},
    {"label": "02 番外", "text": "正文"}
  ]
}
```

Run the builder in a temporary output directory. During publication after review, reconstruct equivalent chapter data from the current Markdown headings and bodies before running it.

## EPUB invariants

- EPUB package version 2.0.
- `mimetype` is the first ZIP member and stored uncompressed.
- One NCX entry and one valid XHTML file per Markdown chapter.
- No visible `toc.xhtml` page or TOC spine item.
- Reading order begins cover → chapter 01.
- Cover appears in OPF metadata and the EPUB 2 guide and is identical to library `cover.jpg`.
- Metadata title and author use normalized values.

## Install safely

- Resolve the exact destination `<作者> - <书名>` before writing.
- For review, install only `cover.jpg` and `<书名> by <作者>.md`.
- For publication, add or update only `<书名> by <作者>.txt` and `<书名> by <作者>.epub`, unless the user separately requests MD or cover changes.
- Do not overwrite an existing work unless the user asked to update it. Preserve unrelated files.
- Do not rename files when renaming a library folder unless explicitly requested.
- Retain or clean temporary work according to the user's latest stated preference.

## Verify before reporting

### Review phase

- Discovered chapter count equals Markdown `##` heading count.
- No empty chapter, trailing login prompt, unwanted duplicate heading, or literal paragraph-leading whitespace remains.
- Markdown first line and filename are `<书名> by <作者>`.
- Destination folder is `<作者> - <书名>` and contains only the authorized files.
- Cover is JPEG, 1080×1440, 300 DPI; report crop, padding, or ImageGen treatment.
- Report preserved special headings and genuine placeholders.

### Publication phase

- Current MD, TXT sections, EPUB XHTML chapters, and NCX points have matching labels and counts.
- MD/TXT first lines and all filenames remain `<书名> by <作者>`.
- TXT has no literal paragraph-leading whitespace.
- EPUB is valid version 2.0, has no visible TOC, begins cover → chapter 01, uses CSS-only `2em` indentation, and embeds the verified cover.
