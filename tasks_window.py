import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox, QComboBox, QTextEdit, QDoubleSpinBox)
from db_connection import get_connection
from report_functions import save_report

class TasksWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Управление задачами ({role})")
        self.resize(1000, 600)
        self.selected_id = None
        self.init_ui()
        self.load_data()
        self.load_combos()
        self.apply_role_restrictions()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Стоимость", "Длительность (дни)", "Прогресс (%)", "Проект"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название задачи")
        row1.addWidget(self.name_input)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Описание:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Введите описание задачи")
        row2.addWidget(self.desc_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Стоимость:"))
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        row3.addWidget(self.cost_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Длительность (дни):"))
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setMinimum(0.1)
        self.duration_input.setMaximum(9999)
        self.duration_input.setValue(1)
        row4.addWidget(self.duration_input)
        form_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Прогресс (%):"))
        self.progress_input = QSpinBox()
        self.progress_input.setMinimum(0)
        self.progress_input.setMaximum(100)
        self.progress_input.setValue(0)
        row5.addWidget(self.progress_input)
        form_layout.addLayout(row5)

        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Проект:"))
        self.project_combo = QComboBox()
        row6.addWidget(self.project_combo)
        form_layout.addLayout(row6)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_task)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_task)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_task)
        btn_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_inputs)
        btn_layout.addWidget(self.clear_btn)

        self.report_btn = QPushButton("Создать отчет")
        self.report_btn.clicked.connect(self.generate_report)
        btn_layout.addWidget(self.report_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def load_combos(self):
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_project, name FROM Projects ORDER BY name")
            projects = cursor.fetchall()
            self.project_combo.clear()
            for proj in projects:
                self.project_combo.addItem(proj[1], proj[0])
        except Exception as e:
            print(f"Ошибка загрузки проектов: {e}")
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
            cursor.execute("""SELECT t.id_task, t.name, t.description, t.costs, t.duration, t.progress, p.name
                              FROM Tasks t
                              LEFT JOIN Projects p ON t.project_id = p.id_project
                              ORDER BY t.id_task;""")
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
            self.cost_input.setText(self.table.item(row, 3).text())
            self.duration_input.setValue(float(self.table.item(row, 4).text()))
            self.progress_input.setValue(int(self.table.item(row, 5).text()))
            project = self.table.item(row, 6).text()
            for i in range(self.project_combo.count()):
                if self.project_combo.itemText(i) == project:
                    self.project_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            pass

    def add_task(self):
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        cost = self.cost_input.text().strip()
        duration = self.duration_input.value()
        progress = self.progress_input.value()
        project_id = self.project_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название задачи!")
            return
        if not cost:
            QMessageBox.warning(self, "Ошибка", "Введите стоимость!")
            return
        if not project_id:
            QMessageBox.warning(self, "Ошибка", "Выберите проект!")
            return
        try:
            cost = float(cost)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат стоимости!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO Tasks (name, description, costs, duration, progress, project_id)
                           VALUES (%s, %s, %s, %s, %s, %s)""", (name, description, cost, duration, progress, project_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Задача добавлена!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_task(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу!")
            return
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        cost = self.cost_input.text().strip()
        duration = self.duration_input.value()
        progress = self.progress_input.value()
        project_id = self.project_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название задачи!")
            return
        if not cost:
            QMessageBox.warning(self, "Ошибка", "Введите стоимость!")
            return
        try:
            cost = float(cost)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат стоимости!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE Tasks SET name = %s, description = %s, costs = %s, duration = %s, progress = %s, project_id = %s
                           WHERE id_task = %s""", (name, description, cost, duration, progress, project_id, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_task(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить эту задачу?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Tasks WHERE id_task = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Задача удалена!")
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
        self.cost_input.clear()
        self.duration_input.setValue(1)
        self.progress_input.setValue(0)
        if self.project_combo.count() > 0:
            self.project_combo.setCurrentIndex(0)

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
            cursor.execute("""SELECT t.id_task, t.name, t.description, t.costs, t.duration, t.progress, p.name
                              FROM Tasks t
                              LEFT JOIN Projects p ON t.project_id = p.id_project
                              ORDER BY t.id_task;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 70 + "\n"
            report_text += "ОТЧЕТ ПО ЗАДАЧАМ\n"
            report_text += "=" * 70 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего задач: {len(rows)}\n\n"

            for row in rows:
                id_t, name, desc, cost, duration, progress, project = row
                report_text += f"Задача ID: {id_t}\n"
                report_text += f"Название: {name}\n"
                report_text += f"Описание: {desc if desc else 'Нет'}\n"
                report_text += f"Стоимость: {float(cost):,.2f} руб.\n"
                report_text += f"Длительность: {float(duration):.1f} дней\n"
                report_text += f"Прогресс: {progress}%\n"
                report_text += f"Проект: {project}\n"
                report_text += "-" * 50 + "\n"

            success, message = save_report(report_text, "tasks_report")
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
        preview.setWindowTitle("Просмотр отчета - Задачи")
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