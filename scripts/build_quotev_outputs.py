#!/usr/bin/env python3
"""Build clean MD, TXT, cover.jpg, and Kindle-friendly EPUB 2.0 files."""

import argparse
import html
import json
import re
import shutil
import struct
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


UI_TRAILER = re.compile(r"\n?登录或注册并选择[“\"]添加到库[”\"]以关注此故事的更新\s*$")


def x(value):
    return html.escape(str(value), quote=True)


def clean_text(value):
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
    return UI_TRAILER.sub("", text).strip()


def paragraphs(text):
    blocks = re.split(r"\n\s*\n", text)
    return "\n".join(f"<p>{'<br/>'.join(x(line) for line in block.splitlines())}</p>" for block in blocks if block.strip())


def jpeg_size(path):
    data = Path(path).read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError("cover must be a JPEG")
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        pos += 2
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        length = struct.unpack(">H", data[pos:pos + 2])[0]
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
            return width, height
        pos += length
    raise ValueError("cannot read JPEG dimensions")


def validate_data(data):
    for key in ("title", "author", "display_title", "chapters"):
        if not data.get(key):
            raise ValueError(f"missing required field: {key}")
    if "/" in data["display_title"] or "\x00" in data["display_title"]:
        raise ValueError("display_title is unsafe as a filename")
    if not isinstance(data["chapters"], list):
        raise ValueError("chapters must be a list")
    for index, chapter in enumerate(data["chapters"], 1):
        if not chapter.get("label") or "text" not in chapter:
            raise ValueError(f"invalid chapter {index}")


def make_xhtml(title, body):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{x(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>'''


def build_epub(data, cover, target):
    uid = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, data.get('source_url') or data['display_title'])}"
    chapters = data["chapters"]
    manifest = ['<item id="cover-image" href="cover.jpg" media-type="image/jpeg"/>', '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>', '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>', '<item id="css" href="style.css" media-type="text/css"/>']
    spine = ['<itemref idref="cover" linear="no"/>']
    nav = []
    files = {}
    for i, chapter in enumerate(chapters, 1):
        cid = f"chapter{i:03d}"
        href = f"{cid}.xhtml"
        label = clean_text(chapter["label"])
        body = f"<h1>{x(label)}</h1>{paragraphs(clean_text(chapter['text']))}"
        files[href] = make_xhtml(label, body).encode()
        manifest.append(f'<item id="{cid}" href="{href}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{cid}"/>')
        nav.append(f'<navPoint id="nav{i}" playOrder="{i}"><navLabel><text>{x(label)}</text></navLabel><content src="{href}"/></navPoint>')
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{x(data['title'])}</dc:title><dc:creator>{x(data['author'])}</dc:creator><dc:language>zh-CN</dc:language><dc:identifier id="BookId">{x(uid)}</dc:identifier><meta name="cover" content="cover-image"/></metadata><manifest>{''.join(manifest)}</manifest><spine toc="ncx">{''.join(spine)}</spine><guide><reference type="cover" title="Cover" href="cover.xhtml"/><reference type="text" title="Start" href="chapter001.xhtml"/></guide></package>'''
    ncx = f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{x(uid)}"/></head><docTitle><text>{x(data['display_title'])}</text></docTitle><navMap>{''.join(nav)}</navMap></ncx>'''
    cover_xhtml = make_xhtml(data["display_title"], '<div class="cover"><img src="cover.jpg" alt="cover"/></div>')
    container = '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    style = 'body{font-family:serif;line-height:1.7;margin:5%;}h1{text-align:center;font-size:1.35em;margin:1.5em 0;}p{text-indent:2em;margin:.6em 0}.cover{margin:0;text-align:center}.cover img{max-width:100%;max-height:100%}'
    with zipfile.ZipFile(target, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/toc.ncx", ncx)
        zf.writestr("OEBPS/style.css", style)
        zf.writestr("OEBPS/cover.xhtml", cover_xhtml)
        zf.write(cover, "OEBPS/cover.jpg")
        for href, payload in files.items():
            zf.writestr(f"OEBPS/{href}", payload)


def validate_epub(path, chapter_count, cover):
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        if infos[0].filename != "mimetype" or infos[0].compress_type != zipfile.ZIP_STORED:
            raise ValueError("invalid EPUB mimetype entry")
        names = set(zf.namelist())
        if any(name.endswith("toc.xhtml") for name in names):
            raise ValueError("visible TOC page is forbidden")
        for name in names:
            if name.endswith((".xml", ".opf", ".ncx", ".xhtml")):
                ET.fromstring(zf.read(name))
        opf = ET.fromstring(zf.read("OEBPS/content.opf"))
        if opf.attrib.get("version") != "2.0":
            raise ValueError("EPUB package is not version 2.0")
        ns = {"o": "http://www.idpf.org/2007/opf", "n": "http://www.daisy.org/z3986/2005/ncx/"}
        refs = opf.findall("o:spine/o:itemref", ns)
        if len(refs) != chapter_count + 1 or refs[0].attrib.get("idref") != "cover" or refs[1].attrib.get("idref") != "chapter001":
            raise ValueError("invalid EPUB reading order")
        ncx = ET.fromstring(zf.read("OEBPS/toc.ncx"))
        if len(ncx.findall(".//n:navPoint", ns)) != chapter_count:
            raise ValueError("NCX chapter count mismatch")
        if zf.read("OEBPS/cover.jpg") != Path(cover).read_bytes():
            raise ValueError("embedded cover differs from cover.jpg")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    validate_data(data)
    if jpeg_size(args.cover) != (1080, 1440):
        raise ValueError("cover must be exactly 1080x1440 pixels")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    name = data["display_title"]
    chapters = [{"label": clean_text(c["label"]), "text": clean_text(c["text"])} for c in data["chapters"]]
    descriptions = [clean_text(v) for v in data.get("description", []) if clean_text(v)]
    md = [name, ""] + [f"> {line}" for line in descriptions]
    if descriptions:
        md.append("")
    for chapter in chapters:
        md += [f"## {chapter['label']}", "", chapter["text"], ""]
    txt = [name, ""] + descriptions
    if descriptions:
        txt.append("")
    for chapter in chapters:
        txt += ["=" * 40, chapter["label"], "=" * 40, "", chapter["text"], ""]
    (args.output_dir / f"{name}.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")
    (args.output_dir / f"{name}.txt").write_text("\n".join(txt).rstrip() + "\n", encoding="utf-8")
    final_cover = args.output_dir / "cover.jpg"
    shutil.copy2(args.cover, final_cover)
    epub = args.output_dir / f"{name}.epub"
    epub_data = dict(data, chapters=chapters)
    build_epub(epub_data, final_cover, epub)
    validate_epub(epub, len(chapters), final_cover)
    print(json.dumps({"name": name, "chapters": len(chapters), "cover": list(jpeg_size(final_cover)), "epub": "EPUB 2.0 validated", "output_dir": str(args.output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
