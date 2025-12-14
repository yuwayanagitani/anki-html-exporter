import re
import shutil
from pathlib import Path

from anki.collection import Collection  # type: ignore


# ページ全体の最低限の枠組み（ここではグローバルCSSは付けない）
DOC_HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Anki Back Export</title>
  <style>
.card {
    color: #222222;
    background-color: #ffffff;
    line-height: 2;
    font-family: "Yu Gothic UI", "Yu Gothic", "Meiryo",
               "Hiragino Sans", "Noto Sans JP", sans-serif;
    font-size: 18px;
    text-align: left;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 40px;
    box-shadow: 0 0 10px rgba(0,0,0,0.08);
}
.back {
    width: 95%;
    margin: auto;
}
img {
    max-width: 800px;
    max-height: 400px;
}
  </style>
</head>
<body>
"""

DOC_FOOT = """
</body>
</html>
"""


def export_cards_back(col: Collection, card_ids, output_file: Path) -> None:
    """
    ブラウザで選択されたカードIDの一覧から、
    ・card.answer() を使って裏面HTMLをレンダリング
    ・noteのノートタイプCSSを埋め込み
    ・1つのHTMLにまとめて出力
    ・画像は collection.media からコピー
    を行うメイン関数
    """
    media_dir = Path(col.media.dir())
    cards_html = []

    for cid in card_ids:
        card = col.get_card(cid)
        note = card.note()

        # ノートタイプ（モデル）と CSS
        if hasattr(note, "note_type"):
            model = note.note_type()
        else:
            model = note.model()
        css = model.get("css", "")

        # Anki 内部でレンダリングした Answer HTML
        # 通常は front + <hr id="answer"> + back という構造になっている
        full_answer_html = card.answer()

        # 「表面は不要」なので、<hr id="answer"> 以降だけを抜き出す
        back_html = full_answer_html
        m = re.search(r'<hr[^>]*id=["\']answer["\'][^>]*>', full_answer_html)
        if m:
            back_html = full_answer_html[m.end():]
            # 最初の <style>...</style> を削除（外側で model['css'] を入れているので重複するため）
            back_html = re.sub(r"<style.*?</style>", "", back_html, count=1, flags=re.S)

        # デッキ名（おまけ情報。いらなければ空文字でもOK）
        deck_name = ""
        deck = col.decks.get(card.did)
        if deck:
            deck_name = deck.get("name", "")

        # 1カード分のHTMLブロック
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

    # すべて結合して1つのHTMLに
    full_html = DOC_HEAD + "\n".join(cards_html) + DOC_FOOT

    # HTMLファイルを書き出し
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        f.write(full_html)

    # ==== 画像コピー ====
    _copy_images_from_html(full_html, media_dir, output_file.parent)


def _copy_images_from_html(html: str, media_dir: Path, out_dir: Path) -> None:
    """
    HTML 内の src="..." を全て拾って、
    Anki の media フォルダから同じフォルダへコピーする
    """
    # src="〜" にマッチ
    image_names = set(re.findall(r'src="([^"]+)"', html))
    if not image_names:
        return

    if not media_dir.exists():
        return

    for name in image_names:
        src = media_dir / name
        dst = out_dir / name
        if src.exists():
            shutil.copy2(src, dst)
