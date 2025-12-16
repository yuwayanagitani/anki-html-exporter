from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from aqt import gui_hooks, mw
from aqt.qt import (
    QAction,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from .exporter import export_cards_back

ADDON_PACKAGE = __name__

# NOTE:
# - この dict は「デフォルト値」専用（安定したユーザー設定だけ）。
# - 動的データ（履歴/キャッシュ/ログ/カードID一覧など）は絶対に入れない。
DEFAULT_CONFIG: Dict[str, Any] = {
    "01_general": {
        "enabled": True,
    },
    "02_export": {
        "default_filename": "selected_back.html",
        "copy_media_files": True,
    },
    "03_html": {
        "doc_lang": "ja",
        "doc_title": "Anki Back Export",
    },
    "04_images": {
        "img_max_width_px": 800,
        "img_max_height_px": 400,
    },
}


def _deep_merge(defaults: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """defaults をベースに user を上書きした新しい dict を返す（破壊しない）。"""
    out: Dict[str, Any] = {}
    for k, dv in defaults.items():
        uv = user.get(k, None)
        if isinstance(dv, dict) and isinstance(uv, dict):
            out[k] = _deep_merge(dv, uv)
        else:
            out[k] = uv if uv is not None else dv
    return out


def get_config() -> Dict[str, Any]:
    """Anki のユーザー設定（meta.json）を読み、DEFAULT_CONFIG とマージした設定を返す。"""
    try:
        user_conf = mw.addonManager.getConfig(ADDON_PACKAGE)
    except Exception:
        user_conf = None
    if not isinstance(user_conf, dict):
        user_conf = {}
    return _deep_merge(DEFAULT_CONFIG, user_conf)


def _write_config(conf: Dict[str, Any]) -> None:
    """
    GUIからの保存専用。

    ポイント:
    - 「既知キーだけ」を書き出す（不要キー＝キャッシュ等が溜まらない）
    - エクスポート処理中に config を更新しない（常にGUI操作のみで変更）
    """
    sanitized = _deep_merge(DEFAULT_CONFIG, conf)  # defaults 構造に揃える
    try:
        mw.addonManager.writeConfig(ADDON_PACKAGE, sanitized)
    except Exception:
        # 互換性フォールバック（古いAnki向け）
        try:
            mw.addonManager.setConfig(ADDON_PACKAGE, sanitized)
        except Exception:
            pass


# -------------------- Custom Config GUI --------------------

class ConfigDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Back Export - Settings")
        self.setMinimumWidth(560)

        cfg = get_config()

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ---- General ----
        box_general = QGroupBox("General")
        form_g = QFormLayout(box_general)
        form_g.setVerticalSpacing(10)

        self.enabled_cb = QCheckBox()
        self.enabled_cb.setChecked(bool(cfg.get("01_general", {}).get("enabled", True)))
        form_g.addRow("Enable add-on", self.enabled_cb)

        root.addWidget(box_general)

        # ---- Export ----
        box_export = QGroupBox("Export")
        form_e = QFormLayout(box_export)
        form_e.setVerticalSpacing(10)

        self.default_filename = QLineEdit()
        self.default_filename.setText(str(cfg.get("02_export", {}).get("default_filename", "selected_back.html")))
        self.default_filename.setPlaceholderText("selected_back.html")
        form_e.addRow("Default output filename", self.default_filename)

        self.copy_media_cb = QCheckBox("Copy media files next to HTML (recommended)")
        self.copy_media_cb.setChecked(bool(cfg.get("02_export", {}).get("copy_media_files", True)))
        form_e.addRow("", self.copy_media_cb)

        root.addWidget(box_export)

        # ---- Images ----
        box_img = QGroupBox("Images (HTML display)")
        form_i = QFormLayout(box_img)
        form_i.setVerticalSpacing(10)

        self.max_w = QSpinBox()
        self.max_w.setRange(100, 5000)
        self.max_w.setSingleStep(50)
        self.max_w.setValue(int(cfg.get("04_images", {}).get("img_max_width_px", 800)))
        form_i.addRow("Max width (px)", self.max_w)

        self.max_h = QSpinBox()
        self.max_h.setRange(100, 5000)
        self.max_h.setSingleStep(50)
        self.max_h.setValue(int(cfg.get("04_images", {}).get("img_max_height_px", 400)))
        form_i.addRow("Max height (px)", self.max_h)

        root.addWidget(box_img)

        # ---- Note ----
        note = QLabel(
            "Tip: This add-on does NOT store export history/path in config.\n"
            "Only stable user settings are saved, so the config won't grow over time."
        )
        note.setWordWrap(True)
        root.addWidget(note)

        # ---- Buttons ----
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        btns.accepted.connect(self._on_save)
        btns.rejected.connect(self.reject)

        btn_restore = btns.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        if btn_restore:
            btn_restore.clicked.connect(self._on_restore_defaults)

        root.addWidget(btns)

    def _on_restore_defaults(self) -> None:
        self.enabled_cb.setChecked(bool(DEFAULT_CONFIG["01_general"]["enabled"]))
        self.default_filename.setText(str(DEFAULT_CONFIG["02_export"]["default_filename"]))
        self.copy_media_cb.setChecked(bool(DEFAULT_CONFIG["02_export"]["copy_media_files"]))
        self.max_w.setValue(int(DEFAULT_CONFIG["04_images"]["img_max_width_px"]))
        self.max_h.setValue(int(DEFAULT_CONFIG["04_images"]["img_max_height_px"]))

    def _on_save(self) -> None:
        conf: Dict[str, Any] = {
            "01_general": {
                "enabled": bool(self.enabled_cb.isChecked()),
            },
            "02_export": {
                "default_filename": (self.default_filename.text() or "selected_back.html").strip(),
                "copy_media_files": bool(self.copy_media_cb.isChecked()),
            },
            "03_html": dict(DEFAULT_CONFIG["03_html"]),  # 現状GUI未提供（将来拡張用）
            "04_images": {
                "img_max_width_px": int(self.max_w.value()),
                "img_max_height_px": int(self.max_h.value()),
            },
        }
        _write_config(conf)
        QMessageBox.information(self, "Saved", "Settings saved.")
        self.accept()


def _show_config_dialog() -> None:
    dlg = ConfigDialog(mw)
    dlg.exec()


# -------------------- Export entry (Browser context menu) --------------------

def _selected_card_ids(browser) -> list[int]:
    # 互換性: Ankiのバージョンによりメソッド名が異なることがある
    if hasattr(browser, "selected_cards"):
        return list(browser.selected_cards())
    return list(browser.selectedCards())


def run_export_back_from_browser(browser) -> None:
    """ブラウザで選択されたカードだけ、裏面HTMLを完全再現して出力"""
    if not mw.col:
        QMessageBox.critical(browser, "Export HTML", "Collection is not loaded.")
        return

    cfg = get_config()
    if not bool(cfg.get("01_general", {}).get("enabled", True)):
        QMessageBox.information(browser, "Export HTML", "Add-on is disabled in settings.")
        return

    card_ids = _selected_card_ids(browser)
    if not card_ids:
        QMessageBox.information(browser, "Export HTML", "No card selected.")
        return

    default_name = str(cfg.get("02_export", {}).get("default_filename", "selected_back.html")) or "selected_back.html"

    out_path_str, _ = QFileDialog.getSaveFileName(
        browser,
        "Export selected cards (Back) to HTML",
        default_name,
        "HTML files (*.html *.htm);;All files (*.*)",
    )
    if not out_path_str:
        return

    output_file = Path(out_path_str)

    try:
        export_cards_back(mw.col, card_ids, output_file, cfg)
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


def on_browser_will_show_context_menu(browser, menu) -> None:
    cfg = get_config()
    if not bool(cfg.get("01_general", {}).get("enabled", True)):
        return

    act = QAction("Export selected cards (Back) to HTML…", menu)
    act.triggered.connect(lambda _=False, b=browser: run_export_back_from_browser(b))
    menu.addAction(act)


def init_addon() -> None:
    # 「Config」ボタン → カスタムGUI
    try:
        mw.addonManager.setConfigAction(ADDON_PACKAGE, _show_config_dialog)
    except Exception:
        pass

    # 右クリック（コンテキストメニュー）にだけ項目を追加（常設のツールボタンは増やさない）
    try:
        gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)
    except Exception:
        pass


init_addon()
