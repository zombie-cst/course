import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox, QComboBox, QTextEdit)
from db_connection import get_connection
from report_functions import save_report

class RisksWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Управление рисками ({role})")
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
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Вероятность", "Влияние", "Оценка риска", "Статус"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название риска")
        row1.addWidget(self.name_input)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Описание:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Введите описание риска")
        row2.addWidget(self.desc_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Вероятность (0-1):"))
        self.probability_input = QDoubleSpinBox()
        self.probability_input.setMinimum(0)
        self.probability_input.setMaximum(1)
        self.probability_input.setSingleStep(0.05)
        self.probability_input.setValue(0.5)
        row3.addWidget(self.probability_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Влияние (0-1):"))
        self.impact_input = QDoubleSpinBox()
        self.impact_input.setMinimum(0)
        self.impact_input.setMaximum(1)
        self.impact_input.setSingleStep(0.05)
        self.impact_input.setValue(0.5)
        row4.addWidget(self.impact_input)
        form_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Открыт", "В работе", "Закрыт"])
        row5.addWidget(self.status_combo)
        form_layout.addLayout(row5)

        row6 = QHBoxLayout()
        row6.addWidget(QLabel("План реагирования:"))
        self.mitigation_input = QLineEdit()
        self.mitigation_input.setPlaceholderText("Опишите план действий")
        row6.addWidget(self.mitigation_input)
        form_layout.addLayout(row6)

        row7 = QHBoxLayout()
        row7.addWidget(QLabel("Проект:"))
        self.project_combo = QComboBox()
        row7.addWidget(self.project_combo)
        form_layout.addLayout(row7)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_risk)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_risk)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_risk)
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
            cursor.execute("""SELECT r.id_risk, r.name, r.description, r.probability, r.impact, r.risk_score, r.status
                              FROM Risks r
                              ORDER BY r.id_risk;""")
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
            self.probability_input.setValue(float(self.table.item(row, 3).text()))
            self.impact_input.setValue(float(self.table.item(row, 4).text()))
            status = self.table.item(row, 6).text()
            idx = self.status_combo.findText(status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT mitigation_plan, project_id FROM Risks WHERE id_risk = %s", (self.selected_id,))
                data = cursor.fetchone()
                if data:
                    if data[0]:
                        self.mitigation_input.setText(data[0])
                    for i in range(self.project_combo.count()):
                        if self.project_combo.itemData(i) == data[1]:
                            self.project_combo.setCurrentIndex(i)
                            break
                cursor.close()
                conn.close()
        except Exception as e:
            pass

    def add_risk(self):
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        probability = self.probability_input.value()
        impact = self.impact_input.value()
        status = self.status_combo.currentText()
        mitigation = self.mitigation_input.text().strip()
        project_id = self.project_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название риска!")
            return
        if not project_id:
            QMessageBox.warning(self, "Ошибка", "Выберите проект!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO Risks (name, description, probability, impact, status, mitigation_plan, project_id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", (name, description, probability, impact, status, mitigation, project_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Риск добавлен!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_risk(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите риск!")
            return
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        probability = self.probability_input.value()
        impact = self.impact_input.value()
        status = self.status_combo.currentText()
        mitigation = self.mitigation_input.text().strip()
        project_id = self.project_combo.currentData()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название риска!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE Risks SET name = %s, description = %s, probability = %s, impact = %s, status = %s, mitigation_plan = %s, project_id = %s
                           WHERE id_risk = %s""", (name, description, probability, impact, status, mitigation, project_id, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_risk(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите риск!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить этот риск?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Risks WHERE id_risk = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Риск удален!")
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
        self.probability_input.setValue(0.5)
        self.impact_input.setValue(0.5)
        self.status_combo.setCurrentIndex(0)
        self.mitigation_input.clear()
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
            cursor.execute("""SELECT r.id_risk, r.name, r.description, r.probability, r.impact, r.risk_score, r.status, r.mitigation_plan, p.name
                              FROM Risks r
                              LEFT JOIN Projects p ON r.project_id = p.id_project
                              ORDER BY r.risk_score DESC;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 80 + "\n"
            report_text += "ОТЧЕТ ПО РИСКАМ\n"
            report_text += "=" * 80 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего рисков: {len(rows)}\n\n"

            high_risks = [r for r in rows if float(r[5]) >= 0.5]
            if high_risks:
                report_text += f"⚠ ВЫСОКИЕ РИСКИ (оценка ≥ 0.5): {len(high_risks)}\n"
            report_text += "=" * 80 + "\n\n"

            for row in rows:
                id_r, name, desc, prob, impact, score, status, mitigation, project = row
                report_text += f"Риск ID: {id_r}\n"
                report_text += f"Название: {name}\n"
                report_text += f"Описание: {desc if desc else 'Нет'}\n"
                report_text += f"Вероятность: {float(prob):.2f}\n"
                report_text += f"Влияние: {float(impact):.2f}\n"
                report_text += f"Оценка риска: {float(score):.2f}\n"
                report_text += f"Статус: {status}\n"
                report_text += f"План реагирования: {mitigation if mitigation else 'Не указан'}\n"
                report_text += f"Проект: {project}\n"
                if float(score) >= 0.5:
                    report_text += "   ⚠ ВЫСОКИЙ РИСК!\n"
                report_text += "-" * 60 + "\n"

            success, message = save_report(report_text, "risks_report")
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
        preview.setWindowTitle("Просмотр отчета - Риски")
        preview.resize(750, 600)

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