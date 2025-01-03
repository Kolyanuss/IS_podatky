from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLineEdit, QComboBox,
    QCompleter, QFrame, QLabel, QRadioButton, QMessageBox, QStackedLayout
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ui.add_person_ui import AddPersonDialog
from ui.styles import apply_style, apply_styles, get_button_style
from ui.year_box import YearComboBox
from ui.min_salary_ui import MinSalaryDialog
from ui.change_estate_type_ui import EstateTypeDialog
from ui.real_estate_ui import RealEstateWidget

from app.salary_repository import SalaryRepository
from app.real_estate_repository import RealEstateRepository
from app.real_estate_type_repository import RealEstateTypeBaseRepository

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.input_fields = {}
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.estate_repo = RealEstateRepository(db)
        self.type_base_repo = RealEstateTypeBaseRepository(db)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("База оподаткування")
        self.setGeometry(100, 100, 1400, 700)

        apply_styles(self, ["base", "input_field", "label"])

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()

        # Menu Bar
        self.create_menu_bar()

        top_button_layout = self.create_top_button_layout()
        main_layout.addLayout(top_button_layout)
        
        self.stacked_layout = QStackedLayout()
        
        self.estate_widget = RealEstateWidget(self, self.db)
        # self.estate_widget.setParent(self)
        
        # self.land_parcel_layout = LandParcelLayout(self.db)
        # self.land_parcel_layout.setParent(self)

        self.stacked_layout.addWidget(self.estate_widget)
        # stacked_layout.addLayout(self.land_parcel_layout)

        main_layout.addLayout(self.stacked_layout)
        
        central_widget.setLayout(main_layout)
    
    def chnage_table_action(self):
        if self.stacked_layout.currentIndex() == 0:
            self.stacked_layout.setCurrentIndex(1)
        else:
            self.stacked_layout.setCurrentIndex(0)
    
    def create_menu_bar(self):
        """Створення меню бару"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Actions Menu
        actions_menu = QMenu("Actions", self)
        import_action = QAction("Import from file", self)
        export_action = QAction("Export", self)
        restore_action = QAction("Restore DB", self)
        change_value_action = QAction("Change normative monetary value", self)

        actions_menu.addAction(import_action)
        actions_menu.addAction(export_action)
        actions_menu.addAction(restore_action)
        actions_menu.addAction(change_value_action)
        menu_bar.addMenu(actions_menu)

        # About Menu
        about_menu = QMenu("About", self)
        menu_bar.addMenu(about_menu)

    def create_top_button_layout(self):
        """Створення лейауту з кнопками"""
        button_layout = QHBoxLayout()

        # year
        first_Vbox = QVBoxLayout()
        lable =  QLabel("Поточний рік:")
        lable.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                padding: 0px 5px 0px 5px;
                margin: 0px;
                border: none;
            } """)
        self.year_combo_box = YearComboBox()
        self.year_combo_box.currentIndexChanged.connect(self.year_changed)
        first_Vbox.addWidget(lable)
        first_Vbox.addWidget(self.year_combo_box)

        # min salary
        self.min_salary_button = QPushButton()
        self.check_min_salary()
        self.min_salary_button.clicked.connect(self.open_min_salary_dialog)

        # switch table
        switch_table_button = QPushButton("Switch Table")
        switch_table_button.clicked.connect(self.chnage_table_action)
        switch_table_button.setStyleSheet(get_button_style("neutral") + """
                QPushButton {
                min-height: 60px;
            }""")

        # estate types
        self.change_type_button = QPushButton("Типи нерухомості\nвідмінні від земельних ділянок")
        self.check_type_button()
        self.change_type_button.clicked.connect(self.open_change_type_dialog)

        # person management
        add_person_button = QPushButton("Список осіб")
        add_person_button.setStyleSheet(get_button_style("neutral") + """
                QPushButton {
                min-height: 60px;
            }""")
        add_person_button.clicked.connect(self.open_add_person_dialog)

        button_layout.addLayout(first_Vbox)
        button_layout.addWidget(self.min_salary_button)
        button_layout.addWidget(switch_table_button)
        button_layout.addWidget(self.change_type_button)
        button_layout.addWidget(add_person_button)

        return button_layout

    def open_add_person_dialog(self):
        """Відкриття діалогу додавання користувача."""
        current_layout = self.stacked_layout.currentWidget()
        
        self.person_dialog = AddPersonDialog(self.db)
        self.person_dialog.edited_signal.connect(current_layout.update_person_dropdown)
        self.person_dialog.show()
        
    def open_min_salary_dialog(self):
        self.salary_window = MinSalaryDialog(self.db, self.get_current_year())
        self.salary_window.close_signal.connect(self.combo_check)
        self.salary_window.edited_signal.connect(self.edited_global_var_ivent)
        self.salary_window.exec()
    
    def open_change_type_dialog(self):
        self.estate_type_window = EstateTypeDialog(self.db, self.get_current_year())
        self.estate_type_window.close_signal.connect(self.combo_check)
        self.estate_type_window.edited_signal.connect(self.edited_global_var_ivent)
        self.estate_type_window.exec()
    
    def edited_global_var_ivent(self):
        try:
            self.estate_repo.update_all_tax(self.get_current_year())
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося розрахувати нові податки: {e}")
        self.load_data()

    def year_changed(self):
        self.combo_check()
        self.load_data()
    
    def combo_check(self):
        self.stacked_layout.currentWidget().clear_inputs()
        self.check_min_salary()
        self.check_type_button()
    
    def check_min_salary(self):
        if salary := self.salary_repo.get_record_by_id(self.get_current_year()):
            self.min_salary_button.setText(f"Мінімальна зарплата:\n{salary[1]} грн")
            self.min_salary_button.setStyleSheet(get_button_style("success") + """
                QPushButton {
                min-height: 60px;
            }""")
        else:
            self.min_salary_button.setText(f"Мінімальна зарплата:\nНе вказано")
            self.min_salary_button.setStyleSheet(get_button_style("warning") + """
                QPushButton {
                min-height: 60px;
            }""")
    
    def check_type_button(self):
        try:
            records = self.type_base_repo.get_type_rates(self.get_current_year())
            if all(element is not None for sublist in records for element in sublist):
                self.change_type_button.setStyleSheet(get_button_style("success") + """
                    QPushButton {
                    min-height: 60px;
                }""")
            else:
                self.change_type_button.setStyleSheet(get_button_style("warning") + """
                    QPushButton {
                    min-height: 60px;
                }""")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити інформацію: {e}")
               
    def get_current_year(self):
        return int(self.year_combo_box.currentText())

    def load_data(self):
        self.stacked_layout.currentWidget().load_data()