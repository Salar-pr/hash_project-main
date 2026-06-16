import sys
from PyQt6.QtWidgets import QApplication

from db.database import init_extended_db
from ui.login import LoginWindow
from ui.dashboard import DashboardWindow
from ui.admin import AdminWindow


def main():
    init_extended_db()

    app = QApplication(sys.argv)
    app.setApplicationName("HR Portal")

    # این list جلوی garbage collection پنجره رو می‌گیره
    active_window: list = []

    def on_login(username: str, role: str):
        if role == "admin":
            window = AdminWindow(username)
        else:
            window = DashboardWindow(username)

        active_window.clear()
        active_window.append(window)  # reference نگه می‌داره

        login.hide()   # به جای close — اپ زنده می‌مونه
        window.show()

        def on_window_closed():
            active_window.clear()
            login.show()

        window.destroyed.connect(on_window_closed)

    login = LoginWindow()
    login.login_success.connect(on_login)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()