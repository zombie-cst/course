import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QTextEdit, QSpinBox)
from PyQt5.QtCore import QDate
from db_connection import get_connection
from report_functions import save_report

class ProjectsWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Управление проектами ({role})")
        self.resize(1000, 600)
        self.selected_id = None
        self.init_ui()
        self.load_data()
        self.load_employees()
        self.apply_role_restrictions()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Бюджет", "Дата начала", "Дата окончания", "Статус", "Руководитель"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название проекта")
        row1.addWidget(self.name_input)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Описание:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Введите описание проекта")
        row2.addWidget(self.desc_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Бюджет:"))
        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("0.00")
        row3.addWidget(self.budget_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Дата начала:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        row4.addWidget(self.start_date_input)
        form_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Дата окончания:"))
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate().addDays(30))
        self.end_date_input.setCalendarPopup(True)
        row5.addWidget(self.end_date_input)
        form_layout.addLayout(row5)

        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Создан", "Планируется", "Утверждён", "В работе", "Завершён"])
        row6.addWidget(self.status_combo)
        form_layout.addLayout(row6)

        row7 = QHBoxLayout()
        row7.addWidget(QLabel("Руководитель:"))
        self.manager_combo = QComboBox()
        row7.addWidget(self.manager_combo)
        form_layout.addLayout(row7)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_project)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_project)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_project)
        btn_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_inputs)
        btn_layout.addWidget(self.clear_btn)

        self.report_btn = QPushButton("Создать отчет")
        self.report_btn.clicked.connect(self.generate_report)
        btn_layout.addWidget(self.report_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def load_employees(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_employee, full_name FROM Employees ORDER BY full_name")
            employees = cursor.fetchall()
            self.manager_combo.clear()
            self.manager_combo.addItem("Не выбран", None)
            for emp in employees:
                self.manager_combo.addItem(emp[1], emp[0])
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")
        finally:
            cursor.close()
            conn.close()

    def load_data(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT p.id_project, p.name, p.description, p.budget, p.start_date, p.end_date, p.status, e.full_name
                              FROM Projects p
                              LEFT JOIN Employees e ON p.employee_id = e.id_employee
                              ORDER BY p.id_project;""")
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
            self.desc_input.setText(self.table.item(row, 2).text() if self.table.item(row, 2) else "")
            self.budget_input.setText(self.table.item(row, 3).text())

            start_str = self.table.item(row, 4).text()
            start = QDate.fromString(start_str, "yyyy-MM-dd")
            if start.isValid():
                self.start_date_input.setDate(start)

            end_str = self.table.item(row, 5).text()
            end = QDate.fromString(end_str, "yyyy-MM-dd")
            if end.isValid():
                self.end_date_input.setDate(end)

            status = self.table.item(row, 6).text()
            idx = self.status_combo.findText(status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

            manager = self.table.item(row, 7).text()
            for i in range(self.manager_combo.count()):
                if self.manager_combo.itemText(i) == manager:
                    self.manager_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            pass

    def add_project(self):
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        budget = self.budget_input.text().strip()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        manager_id = self.manager_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название проекта!")
            return
        if not budget:
            QMessageBox.warning(self, "Ошибка", "Введите бюджет!")
            return
        try:
            budget = float(budget)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат бюджета!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO Projects (name, description, budget, start_date, end_date, status, employee_id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", (name, description, budget, start_date, end_date, status, manager_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Проект добавлен!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_project(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите проект!")
            return
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        budget = self.budget_input.text().strip()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        manager_id = self.manager_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название проекта!")
            return
        if not budget:
            QMessageBox.warning(self, "Ошибка", "Введите бюджет!")
            return
        try:
            budget = float(budget)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат бюджета!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE Projects SET name = %s, description = %s, budget = %s, start_date = %s, end_date = %s, status = %s, employee_id = %s
                           WHERE id_project = %s""", (name, description, budget, start_date, end_date, status, manager_id, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_project(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите проект!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить этот проект?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Projects WHERE id_project = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Проект удален!")
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
        self.desc_input.clear()
        self.budget_input.clear()
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addDays(30))
        self.status_combo.setCurrentIndex(0)
        if self.manager_combo.count() > 0:
            self.manager_combo.setCurrentIndex(0)

    def apply_role_restrictions(self):
        if self.role == "Сотрудник":
            self.add_btn.setEnabled(True)
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)

    def generate_report(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT p.id_project, p.name, p.description, p.budget, p.start_date, p.end_date, p.status, e.full_name
                              FROM Projects p
                              LEFT JOIN Employees e ON p.employee_id = e.id_employee
                              ORDER BY p.id_project;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 70 + "\n"
            report_text += "ОТЧЕТ ПО ПРОЕКТАМ\n"
            report_text += "=" * 70 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего проектов: {len(rows)}\n\n"

            for row in rows:
                id_p, name, desc, budget, start, end, status, manager = row
                report_text += f"Проект ID: {id_p}\n"
                report_text += f"Название: {name}\n"
                report_text += f"Описание: {desc if desc else 'Нет'}\n"
                report_text += f"Бюджет: {float(budget):,.2f} руб.\n"
                report_text += f"Дата начала: {start}\n"
                report_text += f"Дата окончания: {end}\n"
                report_text += f"Статус: {status}\n"
                report_text += f"Руководитель: {manager if manager else 'Не назначен'}\n"
                report_text += "-" * 50 + "\n"

            success, message = save_report(report_text, "projects_report")
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
        preview.setWindowTitle("Просмотр отчета - Проекты")
        preview.resize(700, 550)

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