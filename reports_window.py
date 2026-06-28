from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, QMessageBox, QFileDialog, QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt
from db_connection import get_connection
from datetime import datetime

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отчеты")
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Генерация отчетов")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        label_acc = QLabel("Отчеты по проекту:")
        label_acc.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(label_acc)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line1)

        self.btn_project_report = QPushButton("Сводный отчёт по проекту")
        self.btn_project_report.clicked.connect(self.report_project)
        layout.addWidget(self.btn_project_report)

        self.btn_evm_report = QPushButton("EVM-отчёт")
        self.btn_evm_report.clicked.connect(self.report_evm)
        layout.addWidget(self.btn_evm_report)

        self.btn_risks_report = QPushButton("Отчёт по рискам")
        self.btn_risks_report.clicked.connect(self.report_risks)
        layout.addWidget(self.btn_risks_report)

        self.btn_tasks_report = QPushButton("Отчёт по задачам")
        self.btn_tasks_report.clicked.connect(self.report_tasks)
        layout.addWidget(self.btn_tasks_report)

        self.btn_pert_report = QPushButton("PERT-отчёт")
        self.btn_pert_report.clicked.connect(self.report_pert)
        layout.addWidget(self.btn_pert_report)

        layout.addStretch()
        self.setLayout(layout)

    def save_report_file(self, report_text, default_filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{default_filename}_{timestamp}.txt"
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", filename, "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                QMessageBox.information(self, "Успех", f"Отчет сохранен:\n{file_path}")
                self.show_report_preview(report_text, default_filename)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def show_report_preview(self, report_text, title_prefix):
        preview = QWidget()
        preview.setWindowTitle(f"Просмотр отчета - {title_prefix}")
        preview.resize(750, 600)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(report_text)
        text_edit.setReadOnly(True)
        text_edit.setFontFamily("Courier New")
        layout.addWidget(text_edit)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(preview.close)
        layout.addWidget(close_btn)
        preview.setLayout(layout)
        preview.show()

    def get_project_summary(self):
        conn = get_connection()
        if not conn:
            return None, "Ошибка подключения к БД"

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT (SELECT COUNT(*) FROM Projects) as total_projects,
                           (SELECT COUNT(*) FROM Projects WHERE status = 'В работе') as active_projects,
                           (SELECT COUNT(*) FROM Projects WHERE status = 'Завершён') as completed_projects,
                           (SELECT COUNT(*) FROM Tasks) as total_tasks,
                           (SELECT COUNT(*) FROM Tasks WHERE progress = 100) as completed_tasks,
                           (SELECT SUM(budget) FROM Projects) as total_budget,
                           (SELECT COUNT(*) FROM Risks WHERE risk_score >= 0.5) as high_risks
                           FROM Projects LIMIT 1;""")
            row = cursor.fetchone()
            return row, None
        except Exception as e:
            return None, str(e)
        finally:
            cursor.close()
            conn.close()

    def report_project(self):
        data, error = self.get_project_summary()
        if error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {error}")
            return

        report_text = "=" * 70 + "\n"
        report_text += "СВОДНЫЙ ОТЧЁТ ПО ПРОЕКТАМ\n"
        report_text += "=" * 70 + "\n\n"
        report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"

        report_text += "СТАТИСТИКА ПРОЕКТОВ:\n"
        report_text += "-" * 50 + "\n"
        report_text += f"Всего проектов: {data[0]}\n"
        report_text += f"  - В работе: {data[1]}\n"
        report_text += f"  - Завершены: {data[2]}\n\n"

        report_text += "СТАТИСТИКА ЗАДАЧ:\n"
        report_text += "-" * 50 + "\n"
        report_text += f"Всего задач: {data[3]}\n"
        report_text += f"  - Выполнено: {data[4]}\n"
        if data[3] > 0:
            completion = (data[4] / data[3]) * 100
            report_text += f"  - Процент выполнения: {completion:.1f}%\n\n"

        report_text += "ФИНАНСЫ:\n"
        report_text += "-" * 50 + "\n"
        report_text += f"Общий бюджет: {float(data[5]):,.2f} руб.\n\n"

        report_text += "РИСКИ:\n"
        report_text += "-" * 50 + "\n"
        report_text += f"Рисков с высокой оценкой (≥0.5): {data[6]}\n"
        report_text += "=" * 70

        self.save_report_file(report_text, "project_summary_report")

    def report_evm(self):
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
            report_text += "ОТЧЕТ ПО EVM-ПОКАЗАТЕЛЯМ\n"
            report_text += "=" * 80 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего записей: {len(rows)}\n\n"

            for row in rows:
                id_e, pv, ev, ac, cpi, spi, date, project = row
                report_text += f"ID: {id_e} | Проект: {project}\n"
                report_text += f"   PV: {float(pv):,.2f} | EV: {float(ev):,.2f} | AC: {float(ac):,.2f}\n"
                report_text += f"   CPI: {float(cpi):.2f}  SPI: {float(spi):.2f}\n"
                report_text += f"   Дата: {date}\n"
                report_text += "-" * 60 + "\n"

            self.save_report_file(report_text, "evm_report")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def report_risks(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT r.id_risk, r.name, r.probability, r.impact, r.risk_score, r.status, r.mitigation_plan, p.name
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

            status_counts = {}
            for row in rows:
                status = row[5]
                status_counts[status] = status_counts.get(status, 0) + 1

            report_text += "Статистика по статусам:\n"
            for status, count in status_counts.items():
                report_text += f"  {status}: {count}\n"
            report_text += "=" * 80 + "\n\n"

            for row in rows:
                id_r, name, prob, impact, score, status, mitigation, project = row
                report_text += f"ID: {id_r} | {name}\n"
                report_text += f"   Вероятность: {float(prob):.2f} | Влияние: {float(impact):.2f}\n"
                report_text += f"   Оценка: {float(score):.2f} {'⚠ ВЫСОКИЙ!' if float(score) >= 0.5 else ''}\n"
                report_text += f"   Статус: {status} | Проект: {project}\n"
                if mitigation:
                    report_text += f"   План: {mitigation}\n"
                report_text += "-" * 60 + "\n"

            self.save_report_file(report_text, "risks_report")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def report_tasks(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT t.id_task, t.name, t.costs, t.duration, t.progress, p.name
                           FROM Tasks t
                           LEFT JOIN Projects p ON t.project_id = p.id_project
                           ORDER BY p.name, t.name;""")
            rows = cursor.fetchall()
            if not rows:
                QMessageBox.warning(self, "Внимание", "Нет данных для отчета!")
                return

            report_text = "=" * 80 + "\n"
            report_text += "ОТЧЕТ ПО ЗАДАЧАМ\n"
            report_text += "=" * 80 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего задач: {len(rows)}\n\n"

            project_tasks = {}
            for row in rows:
                project = row[5] if row[5] else "Без проекта"
                if project not in project_tasks:
                    project_tasks[project] = []
                project_tasks[project].append(row)

            for project, tasks in project_tasks.items():
                report_text += f"\n{project.upper()}:\n"
                report_text += "-" * 60 + "\n"
                total_cost = 0
                completed = 0
                for task in tasks:
                    id_t, name, cost, duration, progress, _ = task
                    report_text += f"  ID:{id_t} | {name}\n"
                    report_text += f"     Стоимость: {float(cost):,.2f} руб. | Длительность: {float(duration):.1f} дн.\n"
                    report_text += f"     Прогресс: {progress}%\n"
                    total_cost += float(cost) if cost else 0
                    if progress == 100:
                        completed += 1
                report_text += f"  Итого задач: {len(tasks)}, выполнено: {completed}\n"
                report_text += f"  Общая стоимость: {total_cost:,.2f} руб.\n"

            self.save_report_file(report_text, "tasks_report")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def report_pert(self):
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

            report_text = "=" * 80 + "\n"
            report_text += "ОТЧЕТ ПО PERT-ОЦЕНКАМ\n"
            report_text += "=" * 80 + "\n\n"
            report_text += f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            report_text += f"Всего оценок: {len(rows)}\n\n"
            report_text += "Формула: Ожидаемая = (Опт + 4*Наиб + Песс) / 6\n"
            report_text += "=" * 80 + "\n\n"

            for row in rows:
                id_p, task, opt, pess, most, exp = row
                report_text += f"ID: {id_p} | Задача: {task}\n"
                report_text += f"   Опт: {float(opt):.1f} | Наиб: {float(most):.1f} | Песс: {float(pess):.1f}\n"
                report_text += f"   Ожидаемая длительность: {float(exp):.2f} дней\n"
                report_text += "-" * 60 + "\n"

            self.save_report_file(report_text, "pert_report")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
        finally:
            cursor.close()
            conn.close()