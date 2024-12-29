from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLineEdit, QComboBox,
    QCompleter, QFrame, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ui.add_person_ui import AddPersonDialog
from ui.styles import apply_styles, get_button_style
from ui.utils import create_CUD_buttons, create_table_widget
from ui.year_box import YearComboBox
from ui.min_salary_ui import MinSalaryDialog
from ui.change_estate_type_ui import EstateTypeDialog

from app.salary_repository import SalaryRepository
from app.real_estate_repository import RealEstateRepository

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.input_fields = {}
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.estate_repo = RealEstateRepository(db)
        self.setWindowTitle("База оподаткування.")
        self.setGeometry(100, 100, 1400, 700)

        apply_styles(self, ["base", "input_field", "label"])

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        top_button_layout = self.create_top_button_layout()
        self.table = create_table_widget(len(self.estate_repo.columns), self.estate_repo.columns, self.on_cell_click)
        action_layout = self.create_action_layouts()
        action_button_layout = create_CUD_buttons(self.add_record, self.update_record, self.delete_record)

        # Menu Bar
        self.create_menu_bar()

        # Combine Layouts
        main_layout.addLayout(top_button_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(action_layout)
        main_layout.addLayout(action_button_layout)
        
        central_widget.setLayout(main_layout)

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
        lable.setStyleSheet("font-size: 18px;")
        self.year_combo_box = YearComboBox()
        self.year_combo_box.currentIndexChanged.connect(self.check_min_salary)
        first_Vbox.addWidget(lable)
        first_Vbox.addWidget(self.year_combo_box)

        # min salary
        self.min_salary_button = QPushButton()
        self.check_min_salary()
        self.min_salary_button.clicked.connect(self.open_min_salary_dialog)

        # switch table
        switch_table_button = QPushButton("Switch Table")
        switch_table_button.setStyleSheet(get_button_style("neutral") + """
                QPushButton {
                min-height: 60px;
            }""")

        # estate types
        self.change_type_button = QPushButton("Типи нерухомості\nвідмінні від земельних ділянок")
        self.change_type_button.setStyleSheet(get_button_style("neutral") + """
                QPushButton {
                min-height: 60px;
            }""")
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

    def create_input_field(self, label_text, input_field):
        """Створення вертикального блоку з міткою та полем вводу"""
        field_layout = QVBoxLayout()
        label = QLabel(label_text)
        
        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        
        return field_layout

    def create_person_dropdown(self):
        person_dropdown = QComboBox()
        person_dropdown.setEditable(True)
        person_dropdown.setPlaceholderText("Select Person")

        # Example data for people
        self.person_list = ["Smith, John", "Doe, Jane", "Brown, Charlie", "Johnson, Emily"]
        person_dropdown.addItems(self.person_list)

        # Add search functionality
        completer = QCompleter(self.person_list, person_dropdown)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        person_dropdown.setCompleter(completer)
        
        return person_dropdown

    def create_action_layouts(self):
        """Створення полів для вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_container.setStyleSheet("""
            #inputContainer {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #dcdde1;
            }
        """)
        
        action_layout = QHBoxLayout(input_container)
        
        person_dropdown = self.create_input_field("Власник нерухомості:", self.create_person_dropdown())
        
        name_input = self.create_input_field("Назва нерухомості:", QLineEdit())

        address_input = self.create_input_field("Адреса нерухомості:", QLineEdit())

        area_input = self.create_input_field("Площа(м^2):", QLineEdit())

        type_dropdown = QComboBox()
        type_dropdown.addItems(["Type 1", "Type 2", "Type 3"])
        type_dropdown = self.create_input_field("Тип нерухомості:", type_dropdown)

        note_input = self.create_input_field("Нотатки:", QLineEdit())

        action_layout.addLayout(person_dropdown)
        action_layout.addLayout(name_input)
        action_layout.addLayout(address_input)
        action_layout.addLayout(area_input)
        action_layout.addLayout(type_dropdown)
        action_layout.addLayout(note_input)

        return input_container

    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""        
        i = 1
        for field in self.input_fields.values():
            field.setText(self.table.item(row, i).text())
            i += 1
        
    def open_add_person_dialog(self):
        """Відкриття діалогу додавання користувача."""
        self.person_dialog = AddPersonDialog(self.db)
        self.person_dialog.show()
        
    def open_min_salary_dialog(self):
        self.salary_window = MinSalaryDialog(self.db, int(self.year_combo_box.currentText()))
        self.salary_window.close_signal.connect(self.check_min_salary)
        self.salary_window.exec()
        
    def check_min_salary(self):
        if salary := self.salary_repo.get_record_by_id(int(self.year_combo_box.currentText())):
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
    
    def open_change_type_dialog(self):
        self.estate_type_window = EstateTypeDialog(self.db, int(self.year_combo_box.currentText()))
        self.estate_type_window.close_signal.connect(self.check_type_button)
        self.estate_type_window.exec()
    
    def check_type_button(self):
        pass
    
    def load_data(self):
        """Завантаження інформації з бази даних"""
        records = self.estate_repo.get_all_record()
        self.table.setRowCount(len(records))
        for row_idx, row in enumerate(records):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
    
    def add_record(self):
        """Додавання запису"""
        pass        

    def update_record(self):
        """Оновлення запису"""
        pass

    def delete_record(self):
        """Видалення запису"""
        pass       
