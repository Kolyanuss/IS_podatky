from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLineEdit, QComboBox,
    QCompleter, QFrame, QLabel, QRadioButton, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ui.add_person_ui import AddPersonDialog
from ui.styles import apply_style, apply_styles, get_button_style
from ui.utils import create_CUD_buttons, create_table_widget, create_Vbox
from ui.year_box import YearComboBox
from ui.min_salary_ui import MinSalaryDialog
from ui.change_estate_type_ui import EstateTypeDialog

from app.salary_repository import SalaryRepository
from app.real_estate_repository import RealEstateRepository
from app.real_estate_type_repository import RealEstateTypeRepository
from app.user_repository import UserRepository

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.input_fields = {}
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.estate_repo = RealEstateRepository(db)
        self.type_repo = RealEstateTypeRepository(db)
        self.user_repo = UserRepository(db)
        self.input_fields = {}
        self.fields_config = [
            ("name", "Назва нерухомості", "Введіть назву*"),
            ("address", "Адреса нерухомості", "Введіть адресу*"),
            ("area", "Площа м^2", "Введіть площу*"),
            ("area_tax", "Площа податку м^2", ""),
            ("tax", "Сума податку (грн)", ""),
            ("paid", "Сплачено?", ""),
            ("owner", "Власник нерухомості", "Виберіть власника*"),
            ("type", "Тип нерухомості", "Виберіть тип нерухомості*"),
            ("notes", "Нотатки", "Ваші нотатки"),
        ]
        self.table_column = ["id", "person_id"] + [row[1] for row in self.fields_config]
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("База оподаткування.")
        self.setGeometry(100, 100, 1400, 700)

        apply_styles(self, ["base", "input_field", "label"])

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        top_button_layout = self.create_top_button_layout()
        self.table = create_table_widget(len(self.table_column), self.table_column, self.on_cell_click)
        self.table.setColumnHidden(1, True)
        edit_layout = self.create_edit_layouts()
        action_button_layout = create_CUD_buttons(self.add_record, self.update_record, self.delete_record)

        # Menu Bar
        self.create_menu_bar()

        # Combine Layouts
        main_layout.addLayout(top_button_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(edit_layout)
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
        lable.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                padding: 0px 5px 0px 5px;
                margin: 0px;
                border: none;
            } """)
        self.year_combo_box = YearComboBox()
        self.year_combo_box.currentIndexChanged.connect(self.combo_check)
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

    def create_person_dropdown(self):
        person_dropdown = QComboBox()
        person_dropdown.setEditable(True)
        person_dropdown.setPlaceholderText("Select Person")

        self.person_data_list = self.user_repo.get_id_and_full_name()
        for person in self.person_data_list:
            person_dropdown.addItem(person[1], person[0])

        # функціонал пошуку
        person_names = [person[1] for person in self.person_data_list]
        completer = QCompleter(person_names, person_dropdown)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        person_dropdown.setCompleter(completer)
        
        return person_dropdown

    def create_edit_layouts(self):
        """Створення полів для вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        apply_style(input_container, "input_container")
        
        action_layout = QHBoxLayout(input_container)
        
        # name address area
        for field_name, label_text, placeholder in self.fields_config[:3]: 
            field_layout, input_field = create_Vbox(label_text, QLineEdit(), placeholder)
            self.input_fields[field_name] = input_field
            action_layout.addLayout(field_layout)
            
        self.input_fields["name"].setMaximumWidth(200)
        self.input_fields["area"].setMaximumWidth(120)

        # paid radio button
        radio_box_layout = QVBoxLayout()
        radio_box_layout.addWidget(QLabel(self.fields_config[5][1]))
        
        toggle_layout = QHBoxLayout()
        yes_button = QRadioButton("Так")
        no_button = QRadioButton("Ні")
        no_button.setChecked(True)  # За замовчуванням вибрано "Ні"
        toggle_layout.addWidget(yes_button)
        toggle_layout.addWidget(no_button)
        yes_button.setStyleSheet("font-size: 14px; padding: 10px 0px 10px 10px;")
        no_button.setStyleSheet("font-size: 14px; padding: 10px 10px 10px 0px;")
        
        radio_box_layout.addLayout(toggle_layout)
        self.input_fields[self.fields_config[5][0]] = toggle_layout
        
        # person dropdown
        person_dropdown, input_field = create_Vbox(self.fields_config[-3][1], self.create_person_dropdown(), self.fields_config[-3][2])
        self.input_fields[self.fields_config[-3][0]] = input_field

        # type dropdown
        type_dropdown = QComboBox()
        type_list = self.type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown, input_field = create_Vbox(self.fields_config[-2][1], type_dropdown)
        self.input_fields[self.fields_config[-2][0]] = input_field

        # note input
        note_input, input_field = create_Vbox(self.fields_config[-1][1], QLineEdit(), self.fields_config[-1][2])
        self.input_fields[self.fields_config[-1][0]] = input_field

        # stack everything together
        action_layout.addLayout(radio_box_layout)
        action_layout.addLayout(person_dropdown)
        action_layout.addLayout(type_dropdown)
        action_layout.addLayout(note_input)

        return input_container
        
    def open_add_person_dialog(self):
        """Відкриття діалогу додавання користувача."""
        self.person_dialog = AddPersonDialog(self.db)
        self.person_dialog.show()
        
    def open_min_salary_dialog(self):
        self.salary_window = MinSalaryDialog(self.db, int(self.year_combo_box.currentText()))
        self.salary_window.close_signal.connect(self.combo_check)
        self.salary_window.exec()
    
    def combo_check(self):
        self.check_min_salary()
        self.load_data()
        self.check_type_button()
    
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
        self.estate_type_window.close_signal.connect(self.combo_check)
        self.estate_type_window.exec()
    
    def check_type_button(self):
        pass
    
    def load_data(self):
        """Завантаження інформації з бази даних в таблицю"""
        records = self.estate_repo.get_all_record_by_year(int(self.year_combo_box.currentText()))
        self.table.setRowCount(len(records))
        for row_idx, row in enumerate(records):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
            
            if self.table.item(row_idx, 5).text() == "":
                continue
            area = float(self.table.item(row_idx, 4).text())
            tax_area_limit = float(self.table.item(row_idx, 5).text())
            
            area_taxable = area - tax_area_limit
            area_taxable = area_taxable if area_taxable > 0 else 0
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(area_taxable))) # col=6 це оподаткована площа
            
            if area_taxable == 0:
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(0))) # col=6 це сума податку
                
            if self.table.item(row_idx, 6).text() == "":
                # calculate tax ?
                pass
                
            
    
    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""        
        # i = 1
        # for field in self.input_fields.values():
        #     field.setText(self.table.item(row, i).text())
        #     i += 1
    
    def clear_inputs(self):
        """Очищення всіх полів введення."""
        for field in self.input_fields.values():
            field.clear()
    
    def get_input_data(self):
        """Отримання даних з полів вводу"""
        input_data = {}

        for field_name, input_widget in self.input_fields.items():
            # Якщо це поле типу QLineEdit
            if isinstance(input_widget, QLineEdit):
                input_data[field_name] = input_widget.text()

            # Якщо це поле типу QComboBox
            elif isinstance(input_widget, QComboBox):
                input_data[field_name] = input_widget.currentText()

            # Якщо це RadioButton (група перемикачів)
            elif isinstance(input_widget, QHBoxLayout):
                for i in range(input_widget.count()):
                    widget = input_widget.itemAt(i).widget()
                    if isinstance(widget, QRadioButton) and widget.isChecked():
                        input_data[field_name] = widget.text()
                        break  # Зупиняємося, якщо знайшли вибраний

        return input_data

    def add_record(self):
        """Додавання запису"""
        data = [field.text() for field in self.get_input_data().values()]

        if all(data[:1]):
            year = int(self.year_combo_box.currentText())
            try:
                self.estate_repo.add_record(year, *data)
                QMessageBox.information(self, "Успіх", "Інформацію про земельну ділянку успішно додано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося додати інформацію про земельну ділянку: {e}")
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def update_record(self):
        """Оновлення запису"""
        pass

    def delete_record(self):
        """Видалення запису"""
        pass       
