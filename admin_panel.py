from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QFrame, QTableWidget, QTableWidgetItem, QDialog, QInputDialog)
from user_functions import register_user
from db_connection import get_connection

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.resize(350, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Панель администратора")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line1)

        self.btn_add_user = QPushButton("Добавить пользователя")
        self.btn_add_user.clicked.connect(self.add_user)
        layout.addWidget(self.btn_add_user)

        self.btn_delete_user = QPushButton("Удалить пользователя")
        self.btn_delete_user.clicked.connect(self.delete_user)
        layout.addWidget(self.btn_delete_user)

        self.btn_view_users = QPushButton("Просмотр пользователей")
        self.btn_view_users.clicked.connect(self.view_users)
        layout.addWidget(self.btn_view_users)

        self.setLayout(layout)

    def add_user(self):
        from registration_window import RegistrationWindow
        self.reg_window = RegistrationWindow()
        self.reg_window.show()

    def delete_user(self):
        username, ok = QInputDialog.getText(self, "Удаление пользователя", "Введите логин пользователя для удаления:")
        if ok and username:
            conn = get_connection()
            if not conn:
                QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = %s AND role != 'Руководитель'", (username,))
                if cursor.rowcount > 0:
                    conn.commit()
                    QMessageBox.information(self, "Успех", f"Пользователь {username} удален")
                else:
                    QMessageBox.warning(self, "Ошибка", "Пользователь не найден или является руководителем")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def view_users(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Список пользователей")
        dialog.resize(400, 300)
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ID", "Логин", "Роль"])
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users ORDER BY id")
            rows = cursor.fetchall()
            table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(val)))
            table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()