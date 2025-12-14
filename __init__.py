from pathlib import Path

from aqt import mw, gui_hooks
from aqt.qt import QAction, QFileDialog, QMessageBox

from .exporter import export_cards_back


def run_export_back_from_browser(browser):
    """ブラウザで選択されたカードだけ、裏面HTMLを完全再現して出力"""

    # カード単位で選択を取得
    card_ids = browser.selectedCards()
    if not card_ids:
        QMessageBox.information(browser, "Export HTML", "No card selected")
        return

    # 出力するHTMLファイルを選択
    out_path_str, _ = QFileDialog.getSaveFileName(
        browser,
        "File name",
        "selected_back.html",
        "HTML files (*.html *.htm);;All files (*.*)",
    )
    if not out_path_str:
        return

    output_file = Path(out_path_str)

    try:
        export_cards_back(mw.col, card_ids, output_file)
    except Exception as e:
        QMessageBox.critical(
            browser,
            "HTML export error",
            f"There was an error while exporting HTML:\n{e}",
        )
        return

    QMessageBox.information(
        browser,
        "HTML export completed",
        f"HTML exported:\n{output_file}",
    )


def on_browser_menus_init(browser):
    """ブラウザのメニューに項目を追加"""
    act = QAction("Export selected cards to HTML", browser)
    act.triggered.connect(lambda _, b=browser: run_export_back_from_browser(b))
    # とりあえず「編集」メニューに追加（好きに変えてOK）
    browser.form.menuEdit.addAction(act)


# ブラウザ起動時にメニューを追加
gui_hooks.browser_menus_did_init.append(on_browser_menus_init)
