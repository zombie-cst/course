import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QTextEdit)
from db_connection import get_connection
from report_functions import save_report

class EmployeesWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Сотрудники ({role})")
        self.resize(900, 550)
        self.selected_id = None
        self.init_ui()
        self.load_data()
        self.apply_role_restrictions()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Должность", "Email", "Телефон"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("ФИО:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ФИО")
        row1.addWidget(self.name_input)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Должность:"))
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Введите должность")
        row2.addWidget(self.position_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.ru")
        row3.addWidget(self.email_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Телефон:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7-999-123-45-67")
        row4.addWidget(self.phone_input)
        form_layout.addLayout(row4)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_employee)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_employee)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_employee)
        btn_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_inputs)
        btn_layout.addWidget(self.clear_btn)

        self.report_btn = QPushButton("Создать отчет")
        self.report_btn.clicked.connect(self.generate_report)
        btn_layout.addWidget(self.report_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def load_data(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT id_employee, full_name, position, email, phone
                              FROM Employees ORDER BY id_employee;""")
            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def select_row(self, row, column):
        try:
            self.selected_id = self.table.item(row, 0).text()
            self.name_input.setText(self.table.item(row, 1).text())
            self.position_input.setText(self.table.item(row, 2).text())
            self.email_input.setText(self.table.item(row, 3).text())
            self.phone_input.setText(self.table.item(row, 4).text())
        except Exception:
            pass

    def add_employee(self):
        if self.role == "Сотрудник":
            QMessageBox.warning(self, "Доступ запрещён", "У вас нет прав для добавления сотрудников!")
            return
        full_name = self.name_input.text().strip()
        position = self.position_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО!")
            return
        if not position:
            QMessageBox.warning(self, "Ошибка", "Введите должность!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO Employees (full_name, position, email, phone)
                           VALUES (%s, %s, %s, %s)""", (full_name, position, email, phone))
            conn.commit()
            QMessageBox.information(self, "Успех", "Сотрудник добавлен!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_employee(self):
        if self.role == "Сотрудник":
            QMessageBox.warning(self, "Доступ запрещён", "У вас нет прав для изменения сотрудников!")
            return
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника!")
            return
        full_name = self.name_input.text().strip()
        position = self.position_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        if not full_name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО!")
            return
        if not position:
            QMessageBox.warning(self, "Ошибка", "Введите должность!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE Employees SET full_name = %s, position = %s, email = %s, phone = %s
                           WHERE id_employee = %s""", (full_name, position, email, phone, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_employee(self):
        if self.role == "Сотрудник":
            QMessageBox.warning(self, "Доступ запрещён", "У вас нет прав для удаления сотрудников!")
            return
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить этого сотрудника?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Employees WHERE id_employee = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Сотрудник удален!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        self.selected_id = None
        self.name_input.clear()
        self.position_input.clear()
        self.email_input.clear()
        self.phone_input.clear()

    def apply_role_restrictions(self):
        if self.role == "Сотрудник":
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.name_input.setReadOnly(True)
            self.position_input.setReadOnly(True)
            self.email_input.setReadOnly(True)
            self.phone_input.setReadOnly(True)

    def generate_report(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT id_employee, full_name, position, email, phone
                              FROM Employees ORDER BY id_employee;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 60 + "\n"
            report_text += "ОТЧЕТ ПО СОТРУДНИКАМ\n"
            report_text += "=" * 60 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего сотрудников: {len(rows)}\n\n"

            for row in rows:
                id_e, name, position, email, phone = row
                report_text += f"ID: {id_e} | {name}\n"
                report_text += f"   Должность: {position}\n"
                report_text += f"   Email: {email if email else 'Не указан'}\n"
                report_text += f"   Телефон: {phone if phone else 'Не указан'}\n"
                report_text += "-" * 40 + "\n"

            success, message = save_report(report_text, "employees_report")
            if success:
                QMessageBox.information(self, "Успех", message)
                self.show_report_preview(report_text)
            else:
                QMessageBox.critical(self, "Ошибка", message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании отчета: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def show_report_preview(self, report_text):
        preview = QWidget()
        preview.setWindowTitle("Просмотр отчета - Сотрудники")
        preview.resize(600, 500)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(report_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(preview.close)
        layout.addWidget(close_btn)
        preview.setLayout(layout)
        preview.show()