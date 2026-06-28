import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QTextEdit, QDateEdit)
from PyQt5.QtCore import QDate
from db_connection import get_connection
from report_functions import save_report

class EVMWindow(QWidget):
    def __init__(self, role="Сотрудник"):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"EVM-показатели ({role})")
        self.resize(1000, 600)
        self.selected_id = None
        self.init_ui()
        self.load_data()
        self.load_combos()
        self.apply_role_restrictions()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "PV (план)", "EV (освоено)", "AC (факт)", "CPI", "SPI", "Дата расчёта", "Проект"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)

        form_layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("PV (плановая стоимость):"))
        self.pv_input = QLineEdit()
        self.pv_input.setPlaceholderText("0.00")
        row1.addWidget(self.pv_input)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("EV (освоенная стоимость):"))
        self.ev_input = QLineEdit()
        self.ev_input.setPlaceholderText("0.00")
        row2.addWidget(self.ev_input)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("AC (фактические затраты):"))
        self.ac_input = QLineEdit()
        self.ac_input.setPlaceholderText("0.00")
        row3.addWidget(self.ac_input)
        form_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Дата расчёта:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        row4.addWidget(self.date_input)
        form_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Проект:"))
        self.project_combo = QComboBox()
        row5.addWidget(self.project_combo)
        form_layout.addLayout(row5)

        main_layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_evm)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_evm)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_evm)
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
            cursor.execute("""SELECT e.id_evm, e.pv, e.ev, e.ac, e.cpi, e.spi, e.calculation_date, p.name
                              FROM EVMData e
                              LEFT JOIN Projects p ON e.project_id = p.id_project
                              ORDER BY e.calculation_date DESC;""")
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
            self.pv_input.setText(self.table.item(row, 1).text())
            self.ev_input.setText(self.table.item(row, 2).text())
            self.ac_input.setText(self.table.item(row, 3).text())
            date_str = self.table.item(row, 6).text()
            date = QDate.fromString(date_str.split()[0], "yyyy-MM-dd")
            if date.isValid():
                self.date_input.setDate(date)
            project = self.table.item(row, 7).text()
            for i in range(self.project_combo.count()):
                if self.project_combo.itemText(i) == project:
                    self.project_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            pass

    def add_evm(self):
        pv = self.pv_input.text().strip()
        ev = self.ev_input.text().strip()
        ac = self.ac_input.text().strip()
        calc_date = self.date_input.date().toString("yyyy-MM-dd")
        project_id = self.project_combo.currentData()
        if not pv or not ev or not ac:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if not project_id:
            QMessageBox.warning(self, "Ошибка", "Выберите проект!")
            return
        try:
            pv = float(pv)
            ev = float(ev)
            ac = float(ac)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат чисел!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO EVMData (pv, ev, ac, calculation_date, project_id)
                           VALUES (%s, %s, %s, %s, %s)""", (pv, ev, ac, calc_date, project_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "EVM-данные добавлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_evm(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите запись!")
            return
        pv = self.pv_input.text().strip()
        ev = self.ev_input.text().strip()
        ac = self.ac_input.text().strip()
        calc_date = self.date_input.date().toString("yyyy-MM-dd")
        project_id = self.project_combo.currentData()
        try:
            pv = float(pv)
            ev = float(ev)
            ac = float(ac)
        except:
            QMessageBox.warning(self, "Ошибка", "Некорректный формат чисел!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE EVMData SET pv = %s, ev = %s, ac = %s, calculation_date = %s, project_id = %s
                           WHERE id_evm = %s""", (pv, ev, ac, calc_date, project_id, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def delete_evm(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Ошибка", "Выберите запись!")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить эту запись?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет соединения с БД")
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM EVMData WHERE id_evm = %s", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Запись удалена!")
            self.clear_inputs()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        self.selected_id = None
        self.pv_input.clear()
        self.ev_input.clear()
        self.ac_input.clear()
        self.date_input.setDate(QDate.currentDate())
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
            cursor.execute("""SELECT e.id_evm, e.pv, e.ev, e.ac, e.cpi, e.spi, e.calculation_date, p.name
                              FROM EVMData e
                              LEFT JOIN Projects p ON e.project_id = p.id_project
                              ORDER BY e.calculation_date DESC;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 80 + "\n"
            report_text += "ОТЧЕТ ПО EVM-ПОКАЗАТЕЛЯМ (Освоенный объём)\n"
            report_text += "=" * 80 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего записей: {len(rows)}\n\n"
            report_text += "ПОКАЗАТЕЛИ:\n"
            report_text += "  CPI = EV / AC (индекс выполнения стоимости)\n"
            report_text += "  SPI = EV / PV (индекс выполнения сроков)\n"
            report_text += "  CPI > 1 - эффективно по затратам\n"
            report_text += "  SPI > 1 - опережение по срокам\n"
            report_text += "=" * 80 + "\n\n"

            for row in rows:
                id_e, pv, ev, ac, cpi, spi, date, project = row
                report_text += f"ID: {id_e} | Проект: {project}\n"
                report_text += f"   PV (план): {float(pv):,.2f} руб.\n"
                report_text += f"   EV (освоено): {float(ev):,.2f} руб.\n"
                report_text += f"   AC (факт): {float(ac):,.2f} руб.\n"
                report_text += f"   CPI: {float(cpi):.2f} "
                if float(cpi) >= 1:
                    report_text += "Хорошо\n"
                else:
                    report_text += "Перерасход\n"
                report_text += f"   SPI: {float(spi):.2f} "
                if float(spi) >= 1:
                    report_text += "Хорошо\n"
                else:
                    report_text += "Отставание\n"
                report_text += f"   Дата расчёта: {date}\n"
                report_text += "-" * 60 + "\n"

            success, message = save_report(report_text, "evm_report")
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
        preview.setWindowTitle("Просмотр отчета - EVM")
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