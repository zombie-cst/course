from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QFrame)
from projects_window import ProjectsWindow
from tasks_window import TasksWindow
from pert_window import PERTWindow
from risks_window import RisksWindow
from evm_window import EVMWindow
from employees_window import EmployeesWindow
from reports_window import ReportsWindow
from change_password_window import ChangePasswordWindow
from admin_panel import AdminPanel

class MainMenu(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.setWindowTitle(f"Главное меню - Управление проектами ({role})")
        self.resize(500, 650)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        user_info = QLabel(f"Пользователь: {self.username}\nРоль: {self.role}")
        user_info.setStyleSheet("font-size: 14px; margin: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(user_info)

        label_projects = QLabel("Управление проектами:")
        label_projects.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(label_projects)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line1)

        self.btn_projects = QPushButton("Проекты")
        self.btn_projects.clicked.connect(self.open_projects)
        layout.addWidget(self.btn_projects)

        self.btn_tasks = QPushButton("Задачи")
        self.btn_tasks.clicked.connect(self.open_tasks)
        layout.addWidget(self.btn_tasks)

        self.btn_pert = QPushButton("PERT-оценки")
        self.btn_pert.clicked.connect(self.open_pert)
        layout.addWidget(self.btn_pert)

        self.btn_risks = QPushButton("Риски")
        self.btn_risks.clicked.connect(self.open_risks)
        layout.addWidget(self.btn_risks)

        self.btn_evm = QPushButton("EVM-показатели")
        self.btn_evm.clicked.connect(self.open_evm)
        layout.addWidget(self.btn_evm)

        layout.addSpacing(10)

        label_reports = QLabel("Отчёты:")
        label_reports.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(label_reports)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        self.btn_reports = QPushButton("Отчёты")
        self.btn_reports.clicked.connect(self.open_reports)
        layout.addWidget(self.btn_reports)

        layout.addSpacing(10)

        label_employees = QLabel("Справочники:")
        label_employees.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(label_employees)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line3)

        self.btn_employees = QPushButton("Сотрудники")
        self.btn_employees.clicked.connect(self.open_employees)
        layout.addWidget(self.btn_employees)

        layout.addSpacing(10)

        label_settings = QLabel("Настройки:")
        label_settings.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(label_settings)

        line4 = QFrame()
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line4)

        self.btn_change_password = QPushButton("Сменить пароль")
        self.btn_change_password.clicked.connect(self.open_change_password)
        layout.addWidget(self.btn_change_password)

        if self.role == "Руководитель":
            self.btn_admin_panel = QPushButton("Панель администратора")
            self.btn_admin_panel.clicked.connect(self.open_admin_panel)
            layout.addWidget(self.btn_admin_panel)

        self.btn_exit = QPushButton("Выйти из системы")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        self.apply_role_restrictions()
        self.setLayout(layout)

    def apply_role_restrictions(self):
        if self.role == "Сотрудник":
            self.btn_employees.setEnabled(True)

    def open_projects(self):
        self.projects_window = ProjectsWindow(self.role)
        self.projects_window.show()

    def open_tasks(self):
        self.tasks_window = TasksWindow(self.role)
        self.tasks_window.show()

    def open_pert(self):
        self.pert_window = PERTWindow(self.role)
        self.pert_window.show()

    def open_risks(self):
        self.risks_window = RisksWindow(self.role)
        self.risks_window.show()

    def open_evm(self):
        self.evm_window = EVMWindow(self.role)
        self.evm_window.show()

    def open_employees(self):
        self.employees_window = EmployeesWindow(self.role)
        self.employees_window.show()

    def open_reports(self):
        self.reports_window = ReportsWindow()
        self.reports_window.show()

    def open_change_password(self):
        self.change_password_window = ChangePasswordWindow(self.username)
        self.change_password_window.show()

    def open_admin_panel(self):
        if self.role != "Руководитель":
            QMessageBox.warning(self, "Доступ запрещён", "У вас нет прав для доступа к панели администратора!")
            return
        self.admin_panel = AdminPanel()
        self.admin_panel.show()