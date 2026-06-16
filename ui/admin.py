from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QFrame, QStackedWidget,
    QHeaderView, QMessageBox, QComboBox, QLineEdit, QDialog,
    QFormLayout, QDialogButtonBox,
)
from PyQt6.QtCore import Qt

from connect_DATABASE import delete_user
from db.database import (
    get_all_users, set_user_role,
    get_all_attendance_this_week,
    set_schedule, get_weekly_schedule,
    DAYS,
)
from ui.styles import COLOR, STYLESHEET


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


# ---------------------------------------------------------------------------
# Dialog: Assign Schedule
# ---------------------------------------------------------------------------

class ScheduleDialog(QDialog):

    def __init__(self, username: str, week_start: date, parent=None):
        super().__init__(parent)
        self.username   = username
        self.week_start = week_start
        self.setWindowTitle(f"Assign Schedule — {username}")
        self.setFixedSize(380, 280)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)

        self.cmb_day = QComboBox()
        self.cmb_day.addItems(DAYS)

        self.inp_start = QLineEdit()
        self.inp_start.setPlaceholderText("e.g. 08:00")
        self.inp_start.setFixedHeight(36)

        self.inp_end = QLineEdit()
        self.inp_end.setPlaceholderText("e.g. 17:00")
        self.inp_end.setFixedHeight(36)

        form.addRow("Day:", self.cmb_day)
        form.addRow("Shift Start:", self.inp_start)
        form.addRow("Shift End:", self.inp_end)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)

        lay.addLayout(form)
        lay.addWidget(btns)

    def _save(self):
        day   = self.cmb_day.currentText()
        start = self.inp_start.text().strip()
        end   = self.inp_end.text().strip()

        if not start or not end:
            QMessageBox.warning(self, "Error", "Please fill in shift start and end times.")
            return

        set_schedule(self.username, self.week_start, day, start, end)
        self.accept()


# ---------------------------------------------------------------------------
# Admin Window
# ---------------------------------------------------------------------------

class AdminWindow(QMainWindow):

    def __init__(self, username: str):
        super().__init__()
        self.username   = username
        self.week_start = _monday_of(date.today())
        self.setWindowTitle(f"HR Portal — Admin Panel ({username})")
        self.setMinimumSize(1100, 660)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._refresh_users()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {COLOR['sidebar']};")
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(0)

        brand = QLabel("🏢  Admin Panel")
        brand.setFixedHeight(64)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: bold;")

        self.nav = QListWidget()
        self.nav.addItem(QListWidgetItem("   👥  Employees"))
        self.nav.addItem(QListWidgetItem("   📊  Attendance"))
        self.nav.addItem(QListWidgetItem("   🗓  Schedules"))
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._switch_page)

        user_label = QLabel(f"👤  {self.username}")
        user_label.setStyleSheet("color: #94A3B8; font-size: 12px; padding: 12px 20px;")

        btn_logout = QPushButton("  ⏻  Logout")
        btn_logout.setStyleSheet(
            "background-color: transparent; color: #94A3B8;"
            "text-align: left; padding: 12px 20px; border: none; font-size: 13px;"
        )
        btn_logout.clicked.connect(self.close)

        s_lay.addWidget(brand)
        s_lay.addWidget(self.nav)
        s_lay.addStretch()
        s_lay.addWidget(user_label)
        s_lay.addWidget(btn_logout)

        # ── Stack ─────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_employees_page())
        self.stack.addWidget(self._build_attendance_page())
        self.stack.addWidget(self._build_schedules_page())

        main.addWidget(sidebar)
        main.addWidget(self.stack)

    # ------------------------------------------------------------------
    # Employees Page
    # ------------------------------------------------------------------

    def _build_employees_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        header = QLabel("Employee Management")
        header.setObjectName("title")

        self.tbl_users = QTableWidget()
        self.tbl_users.setColumnCount(4)
        self.tbl_users.setHorizontalHeaderLabels(["ID", "Username", "Role", "Registered"])
        self.tbl_users.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_users.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_users.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_users.verticalHeader().setVisible(False)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_promote = QPushButton("⬆  Promote to Admin")
        btn_promote.setObjectName("btn_secondary")
        btn_promote.clicked.connect(lambda: self._change_role("admin"))

        btn_demote = QPushButton("⬇  Set as Employee")
        btn_demote.setObjectName("btn_secondary")
        btn_demote.clicked.connect(lambda: self._change_role("employee"))

        btn_delete = QPushButton("🗑  Delete User")
        btn_delete.setObjectName("btn_danger")
        btn_delete.clicked.connect(self._delete_selected_user)

        btn_row.addWidget(btn_promote)
        btn_row.addWidget(btn_demote)
        btn_row.addStretch()
        btn_row.addWidget(btn_delete)

        lay.addWidget(header)
        lay.addWidget(self.tbl_users)
        lay.addLayout(btn_row)

        return page

    # ------------------------------------------------------------------
    # Attendance Page
    # ------------------------------------------------------------------

    def _build_attendance_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        header = QLabel("All Employees — Weekly Attendance")
        header.setObjectName("title")

        nav_row = QHBoxLayout()
        btn_prev = QPushButton("← Previous Week")
        btn_prev.setObjectName("btn_secondary")
        btn_prev.setFixedWidth(150)
        btn_prev.clicked.connect(self._prev_week)

        self.lbl_week = QLabel()
        self.lbl_week.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_week.setStyleSheet(f"font-weight: bold; color: {COLOR['text_main']};")

        btn_next = QPushButton("Next Week →")
        btn_next.setObjectName("btn_secondary")
        btn_next.setFixedWidth(150)
        btn_next.clicked.connect(self._next_week)

        nav_row.addWidget(btn_prev)
        nav_row.addWidget(self.lbl_week)
        nav_row.addWidget(btn_next)

        self.tbl_attendance = QTableWidget()
        self.tbl_attendance.setColumnCount(5)
        self.tbl_attendance.setHorizontalHeaderLabels(
            ["Username", "Date", "Clock In", "Clock Out", "Hours"]
        )
        self.tbl_attendance.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_attendance.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_attendance.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_attendance.verticalHeader().setVisible(False)

        lay.addWidget(header)
        lay.addLayout(nav_row)
        lay.addWidget(self.tbl_attendance)

        return page

    # ------------------------------------------------------------------
    # Schedules Page
    # ------------------------------------------------------------------

    def _build_schedules_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        header = QLabel("Assign Weekly Schedules")
        header.setObjectName("title")
        sub = QLabel("Select an employee from the list, then assign their shifts.")
        sub.setObjectName("subtitle")

        content = QHBoxLayout()
        content.setSpacing(20)

        # Employee list
        self.lst_emp = QListWidget()
        self.lst_emp.setFixedWidth(200)
        self.lst_emp.setStyleSheet(
            f"background-color: {COLOR['card']}; color: {COLOR['text_main']};"
            f"border: 1px solid {COLOR['border']}; border-radius: 8px; font-size: 13px;"
        )
        self.lst_emp.currentRowChanged.connect(self._on_employee_selected)

        # Schedule table
        right = QVBoxLayout()
        right.setSpacing(10)

        self.tbl_sched = QTableWidget()
        self.tbl_sched.setColumnCount(3)
        self.tbl_sched.setHorizontalHeaderLabels(["Day", "Shift Start", "Shift End"])
        self.tbl_sched.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_sched.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_sched.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_sched.verticalHeader().setVisible(False)

        btn_assign = QPushButton("＋  Assign Shift")
        btn_assign.setFixedWidth(160)
        btn_assign.clicked.connect(self._assign_shift)

        right.addWidget(self.tbl_sched)
        right.addWidget(btn_assign)

        content.addWidget(self.lst_emp)
        content.addLayout(right)

        lay.addWidget(header)
        lay.addWidget(sub)
        lay.addLayout(content)

        return page

    # ------------------------------------------------------------------
    # Data Refresh
    # ------------------------------------------------------------------

    def _refresh_users(self):
        users = get_all_users()
        self.tbl_users.setRowCount(len(users))
        self.lst_emp.clear()

        for row, u in enumerate(users):
            self.tbl_users.setItem(row, 0, QTableWidgetItem(str(u["id"])))
            self.tbl_users.setItem(row, 1, QTableWidgetItem(u["username"]))
            self.tbl_users.setItem(row, 2, QTableWidgetItem(u["role"]))
            self.tbl_users.setItem(row, 3, QTableWidgetItem(str(u["created_at"])[:10]))
            self.lst_emp.addItem(u["username"])

    def _refresh_attendance(self):
        week_end = self.week_start + timedelta(days=6)
        self.lbl_week.setText(
            f"{self.week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}"
        )
        records = get_all_attendance_this_week(self.week_start)
        self.tbl_attendance.setRowCount(len(records))

        for row, rec in enumerate(records):
            self.tbl_attendance.setItem(row, 0, QTableWidgetItem(rec["username"]))
            self.tbl_attendance.setItem(row, 1, QTableWidgetItem(rec["date"]))
            self.tbl_attendance.setItem(row, 2, QTableWidgetItem(rec["clock_in"]))
            self.tbl_attendance.setItem(row, 3, QTableWidgetItem(rec["clock_out"]))
            self.tbl_attendance.setItem(row, 4, QTableWidgetItem(f"{rec['hours']} h"))

    def _refresh_schedule_for(self, username: str):
        records = get_weekly_schedule(username, self.week_start)
        self.tbl_sched.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.tbl_sched.setItem(row, 0, QTableWidgetItem(rec["day"]))
            self.tbl_sched.setItem(row, 1, QTableWidgetItem(rec["shift_start"]))
            self.tbl_sched.setItem(row, 2, QTableWidgetItem(rec["shift_end"]))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self._refresh_users()
        elif index == 1:
            self._refresh_attendance()
        elif index == 2:
            self._refresh_users()

    def _prev_week(self):
        self.week_start -= timedelta(weeks=1)
        self._refresh_attendance()

    def _next_week(self):
        self.week_start += timedelta(weeks=1)
        self._refresh_attendance()

    def _selected_username(self) -> str | None:
        row = self.tbl_users.currentRow()
        if row < 0:
            return None
        return self.tbl_users.item(row, 1).text()

    def _change_role(self, role: str):
        username = self._selected_username()
        if not username:
            QMessageBox.warning(self, "No Selection", "Please select a user first.")
            return
        set_user_role(username, role)
        self._refresh_users()

    def _delete_selected_user(self):
        username = self._selected_username()
        if not username:
            QMessageBox.warning(self, "No Selection", "Please select a user first.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_user(username)
            self._refresh_users()

    def _on_employee_selected(self, index: int):
        if index < 0:
            return
        username = self.lst_emp.item(index).text()
        self._refresh_schedule_for(username)

    def _assign_shift(self):
        item = self.lst_emp.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Please select an employee first.")
            return
        dlg = ScheduleDialog(item.text(), self.week_start, self)
        if dlg.exec():
            self._refresh_schedule_for(item.text())
