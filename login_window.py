import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from user_functions import login_user
from main_menu import MainMenu

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему - Управление проектами")
        self.resize(350, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Управление проектами")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Логин:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        buttons_layout = QHBoxLayout()
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.open_registration)
        buttons_layout.addWidget(self.register_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return

        success, message, role = login_user(username, password)
        if success:
            QMessageBox.information(self, "Успех", message)
            self.open_main_menu(username, role)
        else:
            QMessageBox.critical(self, "Ошибка", message)

    def open_registration(self):
        from registration_window import RegistrationWindow
        self.reg_window = RegistrationWindow()
        self.reg_window.show()

    def open_main_menu(self, username, role):
        self.close()
        self.main_menu = MainMenu(username, role)
        self.main_menu.show()