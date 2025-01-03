from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLineEdit, QComboBox,
    QCompleter, QFrame, QLabel, QRadioButton, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ui.add_person_ui import AddPersonDialog
from ui.styles import apply_style, apply_styles, get_button_style
from ui.utils import create_CUD_buttons, create_table_widget, create_Vbox, confirm_delete
from ui.year_box import YearComboBox
from ui.min_salary_ui import MinSalaryDialog
from ui.change_estate_type_ui import EstateTypeDialog
from ui.filterable_table_view import FilterableTableWidget

from app.salary_repository import SalaryRepository
from app.real_estate_repository import RealEstateRepository
from app.real_estate_type_repository import RealEstateTypeRepository, RealEstateTypeBaseRepository
from app.user_repository import UserRepository

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.input_fields = {}
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.estate_repo = RealEstateRepository(db)
        self.type_repo = RealEstateTypeRepository(db)
        self.type_base_repo = RealEstateTypeBaseRepository(db)
        self.user_repo = UserRepository(db)
        self.input_fields = {}
        self.fields_config = [
            ("name", "Назва нерухомості", "Введіть назву*"),
            ("address", "Адреса нерухомості", "Введіть адресу*"),
            ("area", "Площа м^2", "Введіть площу*"),
            ("area_tax", "Площа податку", ""),
            ("tax", "Податок (грн)", ""),
            ("paid", "Сплачено?", ""),
            ("owner", "Власник нерухомості", "Виберіть власника*"),
            ("type", "Тип нерухомості", "Виберіть тип нерухомості*"),
            ("notes", "Нотатки", "Ваші нотатки"),
        ]
        self.table_column = ["id", "person_id"] + [row[1] for row in self.fields_config]
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("База оподаткування")
        self.setGeometry(100, 100, 1400, 700)

        apply_styles(self, ["base", "input_field", "label"])

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        top_button_layout = self.create_top_button_layout()
        
        self.table = FilterableTableWidget(self.table_column, [0,1], self.on_cell_click, [4,5,6])
        for i in [4,5,6,7]:
            self.table.table.horizontalHeader().resizeSection(i,75)
            
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

    def create_person_dropdown(self):
        person_dropdown = QComboBox()
        person_dropdown.setEditable(True)
        person_dropdown.setPlaceholderText(self.fields_config[-3][2])
        person_dropdown.setCurrentIndex(-1)

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
        person_dropdown, input_field = create_Vbox(self.fields_config[-3][1], self.create_person_dropdown())
        self.input_fields[self.fields_config[-3][0]] = input_field

        # type dropdown
        type_dropdown = QComboBox()
        type_list = self.type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown.setPlaceholderText("Тип нерухомості")
        type_dropdown.setCurrentIndex(-1)
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
        self.person_dialog.edited_signal.connect(self.users_edited_ivent)
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
    
    def users_edited_ivent(self):
        person_dropdown:QComboBox = self.input_fields["owner"]
        person_dropdown.clear()
        self.person_data_list = self.user_repo.get_id_and_full_name()
        for person in self.person_data_list:
            person_dropdown.addItem(person[1], person[0])

        # функціонал пошуку
        person_names = [person[1] for person in self.person_data_list]
        completer = QCompleter(person_names, person_dropdown)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        person_dropdown.setCompleter(completer)
    
    def combo_check(self):
        self.clear_inputs()
        self.check_min_salary()
        self.check_type_button()
        self.load_data()
    
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
    
    def load_data(self):
        """Завантаження інформації з бази даних в таблицю"""
        self.table.clearSelection()
        self.table.clear_rows()
        records = self.estate_repo.get_all_record_by_year(self.get_current_year())
        
        [self.table.add_row(row) for row in records]
                
    def get_current_year(self):
        return int(self.year_combo_box.currentText())
    
    def on_cell_click(self, model_index):
        """Заповнення полів вводу даними вибраного рядка."""
        row = model_index.row()
        row_data = self.table.get_row_values_by_index(row)
        
        self.input_fields["name"].setText(row_data[2])
        self.input_fields["address"].setText(row_data[3])
        self.input_fields["area"].setText(row_data[4])
        
        # для QRadioButton (paid)
        for j in range(self.input_fields["paid"].count()):
            widget = self.input_fields["paid"].itemAt(j).widget()
            if isinstance(widget, QRadioButton) and widget.text() == row_data[7]:
                widget.setChecked(True)
                break

        # QComboBox ownner
        index = self.input_fields["owner"].findText(row_data[8])
        if index != -1:
            self.input_fields["owner"].setCurrentIndex(index)

        # QComboBox type
        type_name = row_data[9].split(" (")[0]
        index = self.input_fields["type"].findText(type_name)
        if index != -1:
            self.input_fields["type"].setCurrentIndex(index)
        
        self.input_fields["notes"].setText(row_data[10])

    def clear_inputs(self):
        """Очищення всіх полів введення."""
        for field in self.input_fields.values():
            if isinstance(field, QHBoxLayout):
                field.itemAt(1).widget().setChecked(True) # встановлюємо значення "Ні" в статусі оплати
                continue
            if isinstance(field, QComboBox):
                field.setCurrentIndex(-1)
                continue
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
                if input_widget.currentData():
                    input_data[field_name] = input_widget.currentData()
                else:
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
        data = [field for field in self.get_input_data().values()]

        if all(data[:-1]):
            try:
                float(data[2])
            except:
                QMessageBox.warning(self, "Помилка", "Значення площі повинно бути числом!")
                return
            year = self.get_current_year()
            try:
                self.estate_repo.add_record(year, *data)
                # QMessageBox.information(self, "Успіх", "Інформацію про нерухомість успішно додано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Щось пішло не так: {e}")
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def update_record(self):
        """Оновлення запису"""
        selected_row = self.table.get_current_row_index()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для оновлення!")
            return
        
        record_id = self.table.get_row_values_by_index(selected_row)[0]
        data = [field for field in self.get_input_data().values()]
        if all(data[:-1]):
            try:
                float(data[2])
            except:
                QMessageBox.warning(self, "Помилка", "Значення площі повинно бути числом!")
                return
            year = self.get_current_year()
            try:
                self.estate_repo.update_record(record_id, year, *data)
                # QMessageBox.information(self, "Успіх", "Інформацію про нерухомість успішно оновлено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Щось пішло не так: {e}")
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def delete_record(self):
        """Видалення запису"""
        selected_row = self.table.get_current_row_index()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення!")
            return
            
        record_id = self.table.get_row_values_by_index(selected_row)[0]
        
        if confirm_delete() == QMessageBox.StandardButton.Yes:
            try:
                self.estate_repo.delete_record(record_id)
                QMessageBox.information(self, "Успіх", "Нерухомість видалено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити інформацію про нерухомість: {e}")
            self.clear_inputs()
            self.load_data()
          
