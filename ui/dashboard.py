from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QFrame, QStackedWidget,
    QHeaderView, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from db.database import (
    clock_in, clock_out,
    get_weekly_attendance, get_today_attendance,
    get_weekly_schedule,
)
from ui.styles import COLOR, STYLESHEET


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


class DashboardWindow(QMainWindow):

    def __init__(self, username: str):
        super().__init__()
        self.username    = username
        self.week_start  = _monday_of(date.today())
        self.setWindowTitle(f"HR Portal — {username}")
        self.setMinimumSize(1000, 640)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._refresh_home()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {COLOR['sidebar']};")
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(0)

        brand = QLabel("🏢  HR Portal")
        brand.setFixedHeight(64)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;"
                            f"background-color: {COLOR['sidebar']};")

        self.nav = QListWidget()
        self.nav.addItem(QListWidgetItem("   🏠  Home"))
        self.nav.addItem(QListWidgetItem("   📅  Weekly Chart"))
        self.nav.addItem(QListWidgetItem("   🗓  Schedule"))
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._switch_page)

        user_label = QLabel(f"👤  {self.username}")
        user_label.setStyleSheet("color: #94A3B8; font-size: 12px; padding: 12px 20px;")

        btn_logout = QPushButton("  ⏻  Logout")
        btn_logout.setStyleSheet(
            f"background-color: transparent; color: #94A3B8;"
            f"text-align: left; padding: 12px 20px; border: none; font-size: 13px;"
        )
        btn_logout.clicked.connect(self._logout)

        s_lay.addWidget(brand)
        s_lay.addWidget(self.nav)
        s_lay.addStretch()
        s_lay.addWidget(user_label)
        s_lay.addWidget(btn_logout)

        # ── Page Stack ────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.page_home     = self._build_home_page()
        self.page_weekly   = self._build_weekly_page()
        self.page_schedule = self._build_schedule_page()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_weekly)
        self.stack.addWidget(self.page_schedule)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    # ------------------------------------------------------------------
    # Home Page
    # ------------------------------------------------------------------

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(20)

        # Header
        header = QLabel(f"Good day, {self.username} 👋")
        header.setObjectName("title")
        sub = QLabel("Here is your attendance status for today.")
        sub.setObjectName("subtitle")

        # Stat cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_in    = self._stat_card("Clock In",  "--:--", COLOR['accent'])
        self.card_out   = self._stat_card("Clock Out", "--:--", COLOR['success'])
        self.card_hours = self._stat_card("Hours Today", "0.0 h", COLOR['warning'])

        cards_row.addWidget(self.card_in)
        cards_row.addWidget(self.card_out)
        cards_row.addWidget(self.card_hours)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_in  = QPushButton("⏱  Clock In")
        self.btn_in.setObjectName("btn_success")
        self.btn_in.setFixedHeight(44)
        self.btn_in.clicked.connect(self._do_clock_in)

        self.btn_out = QPushButton("⏹  Clock Out")
        self.btn_out.setObjectName("btn_danger")
        self.btn_out.setFixedHeight(44)
        self.btn_out.clicked.connect(self._do_clock_out)

        btn_row.addWidget(self.btn_in)
        btn_row.addWidget(self.btn_out)
        btn_row.addStretch()

        lay.addWidget(header)
        lay.addWidget(sub)
        lay.addSpacing(8)
        lay.addLayout(cards_row)
        lay.addLayout(btn_row)
        lay.addStretch()

        return page

    def _stat_card(self, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {COLOR['card']}; border-radius: 10px;"
            f"border: 1px solid {COLOR['border']};"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 12px; font-weight: bold; border: none;")

        val = QLabel(value)
        val.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color}; border: none;")
        val.setObjectName(f"val_{label.replace(' ', '_')}")

        lay.addWidget(lbl)
        lay.addWidget(val)

        card._value_label = val
        return card

    # ------------------------------------------------------------------
    # Weekly Chart Page
    # ------------------------------------------------------------------

    def _build_weekly_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        header = QLabel("Weekly Attendance Chart")
        header.setObjectName("title")

        # Week navigation
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

        # Table
        self.tbl_weekly = QTableWidget()
        self.tbl_weekly.setColumnCount(4)
        self.tbl_weekly.setHorizontalHeaderLabels(["Date", "Clock In", "Clock Out", "Hours Worked"])
        self.tbl_weekly.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_weekly.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_weekly.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_weekly.verticalHeader().setVisible(False)

        # Summary
        self.lbl_total = QLabel("Total hours this week: 0.0 h")
        self.lbl_total.setStyleSheet(f"font-weight: bold; color: {COLOR['accent']}; font-size: 14px;")

        lay.addWidget(header)
        lay.addLayout(nav_row)
        lay.addWidget(self.tbl_weekly)
        lay.addWidget(self.lbl_total)

        return page

    # ------------------------------------------------------------------
    # Schedule Page
    # ------------------------------------------------------------------

    def _build_schedule_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLOR['bg']};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        header = QLabel("My Weekly Schedule")
        header.setObjectName("title")
        sub = QLabel("Shift times assigned by your manager.")
        sub.setObjectName("subtitle")

        self.tbl_schedule = QTableWidget()
        self.tbl_schedule.setColumnCount(3)
        self.tbl_schedule.setHorizontalHeaderLabels(["Day", "Shift Start", "Shift End"])
        self.tbl_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_schedule.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_schedule.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_schedule.verticalHeader().setVisible(False)

        lay.addWidget(header)
        lay.addWidget(sub)
        lay.addWidget(self.tbl_schedule)
        lay.addStretch()

        return page

    # ------------------------------------------------------------------
    # Data Refresh
    # ------------------------------------------------------------------

    def _refresh_home(self):
        rec = get_today_attendance(self.username)
        if rec:
            self.card_in._value_label.setText(rec["clock_in"])
            self.card_out._value_label.setText(rec["clock_out"])
            self.card_hours._value_label.setText(f"{rec['hours']} h")
        else:
            self.card_in._value_label.setText("--:--")
            self.card_out._value_label.setText("--:--")
            self.card_hours._value_label.setText("0.0 h")

    def _refresh_weekly(self):
        week_end = self.week_start + timedelta(days=6)
        self.lbl_week.setText(
            f"{self.week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}"
        )

        records = get_weekly_attendance(self.username, self.week_start)
        self.tbl_weekly.setRowCount(len(records))
        total = 0.0

        for row, rec in enumerate(records):
            self.tbl_weekly.setItem(row, 0, QTableWidgetItem(rec["date"]))
            self.tbl_weekly.setItem(row, 1, QTableWidgetItem(rec["clock_in"]))
            self.tbl_weekly.setItem(row, 2, QTableWidgetItem(rec["clock_out"]))
            self.tbl_weekly.setItem(row, 3, QTableWidgetItem(f"{rec['hours']} h"))
            total += rec["hours"]

        self.lbl_total.setText(f"Total hours this week: {round(total, 2)} h")

    def _refresh_schedule(self):
        records = get_weekly_schedule(self.username, self.week_start)
        self.tbl_schedule.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.tbl_schedule.setItem(row, 0, QTableWidgetItem(rec["day"]))
            self.tbl_schedule.setItem(row, 1, QTableWidgetItem(rec["shift_start"]))
            self.tbl_schedule.setItem(row, 2, QTableWidgetItem(rec["shift_end"]))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self._refresh_home()
        elif index == 1:
            self._refresh_weekly()
        elif index == 2:
            self._refresh_schedule()

    def _prev_week(self):
        self.week_start -= timedelta(weeks=1)
        self._refresh_weekly()

    def _next_week(self):
        self.week_start += timedelta(weeks=1)
        self._refresh_weekly()

    def _do_clock_in(self):
        ok, msg = clock_in(self.username)
        QMessageBox.information(self, "Clock In", msg) if ok else QMessageBox.warning(self, "Clock In", msg)
        self._refresh_home()

    def _do_clock_out(self):
        ok, msg = clock_out(self.username)
        QMessageBox.information(self, "Clock Out", msg) if ok else QMessageBox.warning(self, "Clock Out", msg)
        self._refresh_home()

    def _logout(self):
        self.close()
