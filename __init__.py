from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from aqt import gui_hooks, mw
from aqt.qt import (
    QAction,
    QCheckBox,
    QComboBox,
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

from .exporter import export_cards_html

ADDON_PACKAGE = __name__

# 安定したユーザー設定だけを持つ（増殖する情報＝履歴/キャッシュ/ログ/最後のパスは入れない）
DEFAULT_CONFIG: Dict[str, Any] = {
    "01_general": {
        "enabled": True,
    },
    "02_export": {
        # "front" / "back" / "both"
        "export_mode": "back",
        "default_filename": "selected_export.html",
        "copy_media_files": True,
    },
    "03_html": {
        "doc_lang": "ja",
        "doc_title": "Anki HTML Export",
    },
    "04_images": {
        "img_max_width_px": 800,
        "img_max_height_px": 400,
    },
}


def _deep_merge(defaults: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, dv in defaults.items():
        uv = user.get(k, None)
        if isinstance(dv, dict) and isinstance(uv, dict):
            out[k] = _deep_merge(dv, uv)
        else:
            out[k] = uv if uv is not None else dv
    return out


def get_config() -> Dict[str, Any]:
    try:
        user_conf = mw.addonManager.getConfig(ADDON_PACKAGE)
    except Exception:
        user_conf = None
    if not isinstance(user_conf, dict):
        user_conf = {}
    return _deep_merge(DEFAULT_CONFIG, user_conf)


def _write_config(conf: Dict[str, Any]) -> None:
    # 既知キーだけに正規化して保存（不要キー＝キャッシュ等を残さない）
    sanitized = _deep_merge(DEFAULT_CONFIG, conf)
    try:
        mw.addonManager.writeConfig(ADDON_PACKAGE, sanitized)
    except Exception:
        try:
            mw.addonManager.setConfig(ADDON_PACKAGE, sanitized)
        except Exception:
            pass


def _selected_card_ids(browser) -> list[int]:
    # 互換性（Ankiの版差）
    if hasattr(browser, "selected_cards"):
        return list(browser.selected_cards())
    return list(browser.selectedCards())


class ConfigDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("HTML Exporter - Settings")
        self.setMinimumWidth(620)

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

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Front only (before <hr id=answer>)", "front")
        self.mode_combo.addItem("Back only (after <hr id=answer>)", "back")
        self.mode_combo.addItem("Both (full answer HTML)", "both")
        cur_mode = str(cfg.get("02_export", {}).get("export_mode", "back")).lower()
        idx = self.mode_combo.findData(cur_mode)
        self.mode_combo.setCurrentIndex(idx if idx >= 0 else 1)
        form_e.addRow("Export mode", self.mode_combo)

        self.default_filename = QLineEdit()
        self.default_filename.setText(str(cfg.get("02_export", {}).get("default_filename", "selected_export.html")))
        self.default_filename.setPlaceholderText("selected_export.html")
        form_e.addRow("Default output filename", self.default_filename)

        self.copy_media_cb = QCheckBox("Copy media files next to HTML")
        self.copy_media_cb.setChecked(bool(cfg.get("02_export", {}).get("copy_media_files", True)))
        form_e.addRow("", self.copy_media_cb)

        root.addWidget(box_export)

        # ---- HTML ----
        box_html = QGroupBox("HTML")
        form_h = QFormLayout(box_html)
        form_h.setVerticalSpacing(10)

        self.doc_lang = QComboBox()
        self.doc_lang.addItems(["ja", "en"])
        self.doc_lang.setCurrentText(str(cfg.get("03_html", {}).get("doc_lang", "ja") or "ja"))
        form_h.addRow("Document language", self.doc_lang)

        self.doc_title = QLineEdit()
        self.doc_title.setText(str(cfg.get("03_html", {}).get("doc_title", "Anki HTML Export") or "Anki HTML Export"))
        form_h.addRow("Document title", self.doc_title)

        root.addWidget(box_html)

        # ---- Images ----
        box_img = QGroupBox("Images (CSS max size)")
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

        note = QLabel(
            "Export runs from Browser right-click menu only.\n"
            "This add-on does NOT store export history/path/cache in config."
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

    def _gather_conf(self) -> Dict[str, Any]:
        return {
            "01_general": {"enabled": bool(self.enabled_cb.isChecked())},
            "02_export": {
                "export_mode": str(self.mode_combo.currentData() or "back"),
                "default_filename": (self.default_filename.text() or "selected_export.html").strip(),
                "copy_media_files": bool(self.copy_media_cb.isChecked()),
            },
            "03_html": {
                "doc_lang": str(self.doc_lang.currentText() or "ja"),
                "doc_title": (self.doc_title.text() or "Anki HTML Export").strip(),
            },
            "04_images": {
                "img_max_width_px": int(self.max_w.value()),
                "img_max_height_px": int(self.max_h.value()),
            },
        }

    def _on_restore_defaults(self) -> None:
        self.enabled_cb.setChecked(bool(DEFAULT_CONFIG["01_general"]["enabled"]))

        idx = self.mode_combo.findData(DEFAULT_CONFIG["02_export"]["export_mode"])
        self.mode_combo.setCurrentIndex(idx if idx >= 0 else 1)

        self.default_filename.setText(str(DEFAULT_CONFIG["02_export"]["default_filename"]))
        self.copy_media_cb.setChecked(bool(DEFAULT_CONFIG["02_export"]["copy_media_files"]))

        self.doc_lang.setCurrentText(str(DEFAULT_CONFIG["03_html"]["doc_lang"]))
        self.doc_title.setText(str(DEFAULT_CONFIG["03_html"]["doc_title"]))

        self.max_w.setValue(int(DEFAULT_CONFIG["04_images"]["img_max_width_px"]))
        self.max_h.setValue(int(DEFAULT_CONFIG["04_images"]["img_max_height_px"]))

    def _on_save(self) -> None:
        _write_config(self._gather_conf())
        QMessageBox.information(self, "Saved", "Settings saved.")
        self.accept()


def _show_config_dialog() -> None:
    dlg = ConfigDialog(mw)
    dlg.exec()


def run_export_from_browser(browser) -> None:
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

    default_name = str(cfg.get("02_export", {}).get("default_filename", "selected_export.html")) or "selected_export.html"
    out_path_str, _ = QFileDialog.getSaveFileName(
        browser,
        "Export selected cards to HTML",
        default_name,
        "HTML files (*.html *.htm);;All files (*.*)",
    )
    if not out_path_str:
        return

    output_file = Path(out_path_str)
    try:
        export_cards_html(mw.col, card_ids, output_file, cfg)
    except Exception as e:
        QMessageBox.critical(browser, "HTML export error", f"There was an error while exporting HTML:\n{e}")
        return

    QMessageBox.information(browser, "HTML export completed", f"HTML exported:\n{output_file}")


def on_browser_will_show_context_menu(browser, menu) -> None:
    cfg = get_config()
    if not bool(cfg.get("01_general", {}).get("enabled", True)):
        return

    act = QAction("Export selected cards to HTML…", menu)
    act.triggered.connect(lambda _=False, b=browser: run_export_from_browser(b))
    menu.addAction(act)


def init_addon() -> None:
    # Add-ons → Config でこのGUIを開く
    try:
        mw.addonManager.setConfigAction(ADDON_PACKAGE, _show_config_dialog)
    except Exception:
        pass

    # ブラウザ右クリックにだけ追加（Tools/常設メニュー追加はしない）
    try:
        gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)
    except Exception:
        pass


init_addon()
