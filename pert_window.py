import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox, QComboBox, QTextEdit)
from db_connection import get_connection
from report_functions import save_report

class PERTWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"PERT-оценки ({role})")
        self.resize(900, 550)
        self.selected_id = None
        self.init_ui()
        self.load_data()
        self.load_combos()
        self.apply_role_restrictions()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Задача", "Оптимистичная", "Пессимистичная", "Наиболее вероятная", "Ожидаемая"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Задача:"))
        self.task_combo = QComboBox()
        row1.addWidget(self.task_combo)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Оптимистичная (дни):"))
        self.optimistic_input = QDoubleSpinBox()
        self.optimistic_input.setMinimum(0.1)
        self.optimistic_input.setMaximum(9999)
        self.optimistic_input.setValue(1)
        row2.addWidget(self.optimistic_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Пессимистичная (дни):"))
        self.pessimistic_input = QDoubleSpinBox()
        self.pessimistic_input.setMinimum(0.1)
        self.pessimistic_input.setMaximum(9999)
        self.pessimistic_input.setValue(1)
        row3.addWidget(self.pessimistic_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Наиболее вероятная (дни):"))
        self.most_likely_input = QDoubleSpinBox()
        self.most_likely_input.setMinimum(0.1)
        self.most_likely_input.setMaximum(9999)
        self.most_likely_input.setValue(1)
        row4.addWidget(self.most_likely_input)
        form_layout.addLayout(row4)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_pert)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_pert)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_pert)
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
            cursor.execute("SELECT id_task, name FROM Tasks ORDER BY name")
            tasks = cursor.fetchall()
            self.task_combo.clear()
            for task in tasks:
                self.task_combo.addItem(task[1], task[0])
        except Exception as e:
            print(f"Ошибка загрузки задач: {e}")
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
            cursor.execute("""SELECT p.id_pert, t.name, p.optimistic, p.pessimistic, p.most_likely, p.expected
                              FROM PERTEvaluations p
                              LEFT JOIN Tasks t ON p.task_id = t.id_task
                              ORDER BY p.id_pert;""")
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
            task_name = self.table.item(row, 1).text()
            for i in range(self.task_combo.count()):
                if self.task_combo.itemText(i) == task_name:
                    self.task_combo.setCurrentIndex(i)
                    break
            self.optimistic_input.setValue(float(self.table.item(row, 2).text()))
            self.pessimistic_input.setValue(float(self.table.item(row, 3).text()))
            self.most_likely_input.setValue(float(self.table.item(row, 4).text()))
        except Exception as e:
            pass

    def add_pert(self):
        task_id = self.task_combo.currentData()
        optimistic = self.optimistic_input.value()
        pessimistic = self.pessimistic_input.value()
        most_likely = self.most_likely_input.value()
        if not task_id:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу!")
            return
        if optimistic > most_likely or pessimistic < most_likely:
            QMessageBox.warning(self, "Ошибка",
                "Проверьте значения: оптимистичная ≤ наиболее вероятная ≤ пессимистичная!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO PERTEvaluations (task_id, optimistic, pessimistic, most_likely)
                           VALUES (%s, %s, %s, %s)""", (task_id, optimistic, pessimistic, most_likely))
            conn.commit()
            QMessageBox.information(self, "Успех", "PERT-оценка добавлена!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_pert(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите запись!")
            return
        task_id = self.task_combo.currentData()
        optimistic = self.optimistic_input.value()
        pessimistic = self.pessimistic_input.value()
        most_likely = self.most_likely_input.value()
        if optimistic > most_likely or pessimistic < most_likely:
            QMessageBox.warning(self, "Ошибка",
                "Проверьте значения: оптимистичная ≤ наиболее вероятная ≤ пессимистичная!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE PERTEvaluations SET task_id = %s, optimistic = %s, pessimistic = %s, most_likely = %s
                           WHERE id_pert = %s""", (task_id, optimistic, pessimistic, most_likely, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_pert(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите запись!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить эту PERT-оценку?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM PERTEvaluations WHERE id_pert = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "PERT-оценка удалена!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        self.selected_id = None
        if self.task_combo.count() > 0:
            self.task_combo.setCurrentIndex(0)
        self.optimistic_input.setValue(1)
        self.pessimistic_input.setValue(1)
        self.most_likely_input.setValue(1)

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
            cursor.execute("""SELECT p.id_pert, t.name, p.optimistic, p.pessimistic, p.most_likely, p.expected
                              FROM PERTEvaluations p
                              LEFT JOIN Tasks t ON p.task_id = t.id_task
                              ORDER BY t.name;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 70 + "\n"
            report_text += "ОТЧЕТ ПО PERT-ОЦЕНКАМ\n"
            report_text += "=" * 70 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего оценок: {len(rows)}\n\n"
            report_text += "Формула PERT: Ожидаемая = (Опт + 4*Наиб + Песс) / 6\n"
            report_text += "=" * 70 + "\n\n"

            for row in rows:
                id_p, task, opt, pess, most, exp = row
                report_text += f"ID: {id_p} | Задача: {task}\n"
                report_text += f"   Оптимистичная: {opt:.1f} дней\n"
                report_text += f"   Пессимистичная: {pess:.1f} дней\n"
                report_text += f"   Наиболее вероятная: {most:.1f} дней\n"
                report_text += f"   Ожидаемая (расчётная): {float(exp):.1f} дней\n"
                report_text += "-" * 50 + "\n"

            success, message = save_report(report_text, "pert_report")
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
        preview.setWindowTitle("Просмотр отчета - PERT")
        preview.resize(650, 500)

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