from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


# ---------------------------------------------------------------------------
# Color Palette  (corporate dark-blue theme)
# ---------------------------------------------------------------------------

COLOR = {
    "bg":          "#F4F6F9",
    "sidebar":     "#1B2A4A",
    "sidebar_sel": "#2E4370",
    "accent":      "#2563EB",
    "accent_dark": "#1D4ED8",
    "success":     "#16A34A",
    "danger":      "#DC2626",
    "warning":     "#D97706",
    "text_main":   "#1E293B",
    "text_muted":  "#64748B",
    "card":        "#FFFFFF",
    "border":      "#E2E8F0",
    "header_bg":   "#1B2A4A",
    "header_text": "#FFFFFF",
}


# ---------------------------------------------------------------------------
# Global Stylesheet
# ---------------------------------------------------------------------------

STYLESHEET = f"""
/* ── Window ────────────────────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {COLOR['bg']};
}}

/* ── Labels ─────────────────────────────────────────────── */
QLabel {{
    color: {COLOR['text_main']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}
QLabel#title {{
    font-size: 22px;
    font-weight: bold;
    color: {COLOR['sidebar']};
}}
QLabel#subtitle {{
    font-size: 13px;
    color: {COLOR['text_muted']};
}}
QLabel#card_title {{
    font-size: 15px;
    font-weight: bold;
    color: {COLOR['text_main']};
}}
QLabel#stat_value {{
    font-size: 28px;
    font-weight: bold;
    color: {COLOR['accent']};
}}

/* ── Input Fields ───────────────────────────────────────── */
QLineEdit {{
    background-color: {COLOR['card']};
    border: 1.5px solid {COLOR['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {COLOR['text_main']};
}}
QLineEdit:focus {{
    border-color: {COLOR['accent']};
}}

/* ── Buttons ────────────────────────────────────────────── */
QPushButton {{
    background-color: {COLOR['accent']};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLOR['accent_dark']};
}}
QPushButton:pressed {{
    background-color: #1E40AF;
}}
QPushButton#btn_secondary {{
    background-color: transparent;
    color: {COLOR['accent']};
    border: 1.5px solid {COLOR['accent']};
}}
QPushButton#btn_secondary:hover {{
    background-color: {COLOR['accent']};
    color: #FFFFFF;
}}
QPushButton#btn_danger {{
    background-color: {COLOR['danger']};
}}
QPushButton#btn_danger:hover {{
    background-color: #B91C1C;
}}
QPushButton#btn_success {{
    background-color: {COLOR['success']};
}}
QPushButton#btn_success:hover {{
    background-color: #15803D;
}}

/* ── Table ──────────────────────────────────────────────── */
QTableWidget {{
    background-color: {COLOR['card']};
    border: 1px solid {COLOR['border']};
    border-radius: 8px;
    gridline-color: {COLOR['border']};
    font-size: 13px;
    color: {COLOR['text_main']};
}}
QTableWidget::item {{
    padding: 8px 12px;
}}
QTableWidget::item:selected {{
    background-color: #DBEAFE;
    color: {COLOR['text_main']};
}}
QHeaderView::section {{
    background-color: {COLOR['sidebar']};
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    padding: 10px 12px;
    border: none;
}}

/* ── Sidebar List ───────────────────────────────────────── */
QListWidget {{
    background-color: {COLOR['sidebar']};
    border: none;
    color: #FFFFFF;
    font-size: 14px;
    outline: 0;
}}
QListWidget::item {{
    padding: 14px 20px;
    border-radius: 0px;
}}
QListWidget::item:selected {{
    background-color: {COLOR['sidebar_sel']};
    color: #FFFFFF;
}}
QListWidget::item:hover {{
    background-color: {COLOR['sidebar_sel']};
}}

/* ── ComboBox ───────────────────────────────────────────── */
QComboBox {{
    background-color: {COLOR['card']};
    border: 1.5px solid {COLOR['border']};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    color: {COLOR['text_main']};
}}
QComboBox:focus {{
    border-color: {COLOR['accent']};
}}

/* ── ScrollBar ──────────────────────────────────────────── */
QScrollBar:vertical {{
    width: 8px;
    background: {COLOR['bg']};
}}
QScrollBar::handle:vertical {{
    background: {COLOR['border']};
    border-radius: 4px;
    min-height: 30px;
}}

/* ── MessageBox ─────────────────────────────────────────── */
QMessageBox {{
    background-color: {COLOR['card']};
}}
"""
