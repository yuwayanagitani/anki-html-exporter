from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from anki.collection import Collection  # type: ignore


def _cfg_get(cfg: Optional[Dict[str, Any]], path: list[str], default: Any) -> Any:
    cur: Any = cfg or {}
    for p in path:
        if not isinstance(cur, dict):
            return default
        if p not in cur:
            return default
        cur = cur[p]
    return cur


def _doc_head(cfg: Optional[Dict[str, Any]] = None) -> str:
    lang = str(_cfg_get(cfg, ["03_html", "doc_lang"], "ja") or "ja")
    title = str(_cfg_get(cfg, ["03_html", "doc_title"], "Anki Back Export") or "Anki Back Export")
    img_w = int(_cfg_get(cfg, ["04_images", "img_max_width_px"], 800) or 800)
    img_h = int(_cfg_get(cfg, ["04_images", "img_max_height_px"], 400) or 400)

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
.card {{
    color: #222222;
    background-color: #ffffff;
    line-height: 2;
    font-family: "Yu Gothic UI", "Yu Gothic", "Meiragino Sans", "Noto Sans JP", sans-serif;
    font-size: 18px;
    text-align: left;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 40px;
    box-shadow: 0 0 10px rgba(0,0,0,0.08);
}}
.back {{
    width: 95%;
    margin: auto;
}}
img {{
    max-width: {img_w}px;
    max-height: {img_h}px;
}}
  </style>
</head>
<body>
"""


DOC_FOOT = """
</body>
</html>
"""


def export_cards_back(col: Collection, card_ids, output_file: Path, cfg: Optional[Dict[str, Any]] = None) -> None:
    """
    ・card.answer() を使って裏面HTMLをレンダリング
    ・noteのノートタイプCSSを埋め込み
    ・1つのHTMLにまとめて出力
    ・（設定により）画像は collection.media からコピー
    """
    media_dir = Path(col.media.dir())
    cards_html: list[str] = []

    for cid in card_ids:
        card = col.get_card(cid)
        note = card.note()

        model = note.note_type() if hasattr(note, "note_type") else note.model()
        css = model.get("css", "")

        full_answer_html = card.answer()

        back_html = full_answer_html
        m = re.search(r'<hr[^>]*id=["\']answer["\'][^>]*>', full_answer_html)
        if m:
            back_html = full_answer_html[m.end():]
            back_html = re.sub(r"<style.*?</style>", "", back_html, count=1, flags=re.S)

        card_block = f"""
<div class="card">
  <style>
{css}
  </style>
  <div class="back">
{back_html}
  </div>
</div>
<br>
"""
        cards_html.append(card_block)

    full_html = _doc_head(cfg) + "\n".join(cards_html) + DOC_FOOT

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        f.write(full_html)

    if bool(_cfg_get(cfg, ["02_export", "copy_media_files"], True)):
        _copy_images_from_html(full_html, media_dir, output_file.parent)


def _copy_images_from_html(html: str, media_dir: Path, out_dir: Path) -> None:
    """
    安全対策:
    - data: / http(s): / file: 等は無視
    - ?query / #hash は除去
    """
    image_srcs = set(re.findall(r'src="([^"]+)"', html))
    if not image_srcs or not media_dir.exists():
        return

    for src_val in image_srcs:
        if not src_val:
            continue
        if src_val.startswith("data:"):
            continue
        if "://" in src_val or src_val.startswith("file:"):
            continue

        name = src_val.split("?", 1)[0].split("#", 1)[0].strip()
        if not name:
            continue

        src = media_dir / name
        dst = out_dir / name
        if src.exists():
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass
