from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from connect_DATABASE import login_user
from db.database import get_user_role
from ui.styles import COLOR


class LoginWindow(QDialog):
    login_success = pyqtSignal(str, str)   # username, role

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HR Portal — Login")
        self.setFixedSize(420, 520)
        self.setModal(True)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(130)
        header.setStyleSheet(f"background-color: {COLOR['sidebar']};")
        h_lay  = QVBoxLayout(header)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("🏢")
        logo.setFont(QFont("Segoe UI", 36))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: #FFFFFF;")

        title = QLabel("HR Portal")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold;")

        h_lay.addWidget(logo)
        h_lay.addWidget(title)

        # ── Form ──────────────────────────────────────────────────────
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {COLOR['card']};")
        form = QVBoxLayout(form_frame)
        form.setContentsMargins(40, 40, 40, 40)
        form.setSpacing(16)

        sign_in_label = QLabel("Sign In")
        sign_in_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLOR['text_main']};")

        sub = QLabel("Enter your credentials to continue")
        sub.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 12px;")

        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet(f"font-weight: bold; color: {COLOR['text_main']};")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Enter username")
        self.input_user.setFixedHeight(40)

        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet(f"font-weight: bold; color: {COLOR['text_main']};")
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Enter password")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setFixedHeight(40)
        self.input_pass.returnPressed.connect(self._handle_login)

        self.btn_login = QPushButton("Sign In")
        self.btn_login.setFixedHeight(42)
        self.btn_login.clicked.connect(self._handle_login)

        self.btn_register = QPushButton("Create Account")
        self.btn_register.setObjectName("btn_secondary")
        self.btn_register.setFixedHeight(42)
        self.btn_register.clicked.connect(self._open_register)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {COLOR['danger']}; font-size: 12px;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form.addWidget(sign_in_label)
        form.addWidget(sub)
        form.addSpacing(8)
        form.addWidget(lbl_user)
        form.addWidget(self.input_user)
        form.addWidget(lbl_pass)
        form.addWidget(self.input_pass)
        form.addSpacing(4)
        form.addWidget(self.btn_login)
        form.addWidget(self.btn_register)
        form.addWidget(self.lbl_error)
        form.addStretch()

        root.addWidget(header)
        root.addWidget(form_frame)

    # ------------------------------------------------------------------
    def _handle_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        if not username or not password:
            self.lbl_error.setText("Please fill in all fields.")
            return

        if login_user(username, password):
            role = get_user_role(username)
            self.login_success.emit(username, role)
            self.hide()
        else:
            self.lbl_error.setText("Invalid username or password.")
            self.input_pass.clear()

    def _open_register(self):
        from ui.register import RegisterWindow
        dlg = RegisterWindow(self)
        dlg.exec()
