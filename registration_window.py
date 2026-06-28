from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox)
from user_functions import register_user


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.resize(350, 280)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Регистрация нового пользователя")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Логин:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Придумайте логин")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Придумайте пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        layout.addWidget(QLabel("Подтвердите пароль:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Повторите пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        layout.addWidget(QLabel("Роль:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Сотрудник", "Руководитель"])
        layout.addWidget(self.role_combo)

        buttons_layout = QHBoxLayout()
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register)
        buttons_layout.addWidget(self.register_btn)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()
        role = self.role_combo.currentText()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
        if len(password) < 3:
            QMessageBox.warning(self, "Ошибка", "Пароль слишком короткий!")
            return

        success, message = register_user(username, password, role)
        if success:
            QMessageBox.information(self, "Успех", message)
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", message)