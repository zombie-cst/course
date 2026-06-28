from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from user_functions import change_password

class ChangePasswordWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Смена пароля")
        self.resize(350, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Пользователь: {self.username}"))
        layout.addWidget(QLabel(""))

        layout.addWidget(QLabel("Текущий пароль:"))
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password_input)

        layout.addWidget(QLabel("Новый пароль:"))
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        layout.addWidget(QLabel("Подтвердите пароль:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        self.change_btn = QPushButton("Сменить пароль")
        self.change_btn.clicked.connect(self.change_password)
        layout.addWidget(self.change_btn)

        self.setLayout(layout)

    def change_password(self):
        old_password = self.old_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm = self.confirm_input.text().strip()
        if not old_password or not new_password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if new_password != confirm:
            QMessageBox.warning(self, "Ошибка", "Новые пароли не совпадают!")
            return
        if len(new_password) < 3:
            QMessageBox.warning(self, "Ошибка", "Новый пароль слишком короткий!")
            return

        success, message = change_password(self.username, old_password, new_password)
        if success:
            QMessageBox.information(self, "Успех", message)
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", message)