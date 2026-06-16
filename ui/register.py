from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt

from connect_DATABASE import register_user
from ui.styles import COLOR


class RegisterWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HR Portal — Create Account")
        self.setFixedSize(420, 500)
        self.setModal(True)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet(f"background-color: {COLOR['sidebar']};")
        h_lay = QVBoxLayout(header)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold;")
        h_lay.addWidget(title)

        # ── Form ──────────────────────────────────────────────────────
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {COLOR['card']};")
        form = QVBoxLayout(form_frame)
        form.setContentsMargins(40, 36, 40, 36)
        form.setSpacing(14)

        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("font-weight: bold;")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Choose a username")
        self.input_user.setFixedHeight(40)

        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("font-weight: bold;")
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Choose a password")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setFixedHeight(40)

        lbl_confirm = QLabel("Confirm Password")
        lbl_confirm.setStyleSheet("font-weight: bold;")
        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("Repeat your password")
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setFixedHeight(40)
        self.input_confirm.returnPressed.connect(self._handle_register)

        self.btn_register = QPushButton("Create Account")
        self.btn_register.setFixedHeight(42)
        self.btn_register.clicked.connect(self._handle_register)

        btn_back = QPushButton("Back to Login")
        btn_back.setObjectName("btn_secondary")
        btn_back.setFixedHeight(42)
        btn_back.clicked.connect(self.reject)

        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setStyleSheet(f"color: {COLOR['danger']}; font-size: 12px;")

        form.addWidget(lbl_user)
        form.addWidget(self.input_user)
        form.addWidget(lbl_pass)
        form.addWidget(self.input_pass)
        form.addWidget(lbl_confirm)
        form.addWidget(self.input_confirm)
        form.addSpacing(4)
        form.addWidget(self.btn_register)
        form.addWidget(btn_back)
        form.addWidget(self.lbl_msg)
        form.addStretch()

        root.addWidget(header)
        root.addWidget(form_frame)

    # ------------------------------------------------------------------
    def _handle_register(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()
        confirm  = self.input_confirm.text()

        if not username or not password or not confirm:
            self._show_error("Please fill in all fields.")
            return

        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return

        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        if register_user(username, password):
            self.lbl_msg.setStyleSheet(f"color: {COLOR['success']}; font-size: 12px;")
            self.lbl_msg.setText("Account created! You can now log in.")
            self.btn_register.setEnabled(False)
        else:
            self._show_error("Username already exists.")

    def _show_error(self, msg: str):
        self.lbl_msg.setStyleSheet(f"color: {COLOR['danger']}; font-size: 12px;")
        self.lbl_msg.setText(msg)
