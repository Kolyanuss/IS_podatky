from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QWidget,
    QCompleter, QFrame, QLabel, QRadioButton, QMessageBox
)
from PyQt6.QtCore import Qt

from ui.styles import apply_style
from ui.utils import create_CUD_buttons, create_Vbox, confirm_delete, get_label
from ui.filterable_table_view import FilterableTableWidget

from app.real_estate_repository import RealEstateRepository
from app.real_estate_type_repository import RealEstateTypeRepository
from app.user_repository import UserRepository

class RealEstateWidget(QWidget):
    def __init__(self, parent, db):
        super().__init__(parent=parent)
        
        self.input_fields = {}
        self.db = db
        self.estate_repo = RealEstateRepository(db)
        self.type_repo = RealEstateTypeRepository(db)
        self.user_repo = UserRepository(db)
        self.input_fields = {}
        self.fields_config = {
            "name": ("Назва нерухомості", "Введіть назву*"),
            "address": ("Адреса нерухомості", "Введіть адресу*"),
            "area": ("Площа\nм^2", "Введіть площу*"),
            "area_tax": ("Площа\nподатку", "Площа податку"),
            "tax": ("Податок\n(грн)", "Податок"),
            "paid": ("Сплачено", "Сплачено"),
            "sum_paid": ("Сплата\nподатку", "Сума сплаченого податку"),
            "owner": ("Власник нерухомості", "Виберіть власника*"),
            "type": ("Тип\nнерухомості", "Виберіть тип*"),
            "notes": ("Нотатки", "Ваші нотатки"),
        }
        self.table_column = ["id", "person_id"] + [value[0] for value in self.fields_config.values()]
        
        
        self.init_ui()
        self.load_data()
        self.table.proxy_model.sort(-1, Qt.SortOrder.AscendingOrder)
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        self.table = FilterableTableWidget(self.table_column, [0,1], self.on_cell_click, [4,5,6,8])
        for i in [4,5,6,7,8]:
            self.table.table.horizontalHeader().resizeSection(i,50)
        self.table.table.horizontalHeader().resizeSection(9,150)
            
        edit_layout = self.create_edit_layouts()
        action_button_layout = create_CUD_buttons(self.add_record, self.update_record, self.delete_record)

        main_layout.addWidget(self.table)
        main_layout.addWidget(edit_layout)
        main_layout.addLayout(action_button_layout)
        
        self.setLayout(main_layout)
    
    def create_edit_layouts(self):
        """Створення полів для вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        apply_style(input_container, "input_container")
        
        vbox = QVBoxLayout(input_container)
        vbox.addWidget(get_label("Редагування:"))
        
        action_layout = QHBoxLayout()
        
        # name address area
        for field_name, text in list(self.fields_config.items())[:3]: 
            field_layout, input_field = create_Vbox(text[0], QLineEdit(), text[1])
            self.input_fields[field_name] = input_field
            action_layout.addLayout(field_layout)
            
        self.input_fields["name"].setMaximumWidth(200)
        self.input_fields["area"].setMaximumWidth(120)

        # paid radio button
        radio_box_layout = QVBoxLayout()
        radio_box_layout.addWidget(QLabel(self.fields_config["paid"][0]))
        
        toggle_layout = QHBoxLayout()
        yes_button = QRadioButton("Так")
        no_button = QRadioButton("Ні")
        no_button.setChecked(True)  # За замовчуванням вибрано "Ні"
        toggle_layout.addWidget(yes_button)
        toggle_layout.addWidget(no_button)
        yes_button.setStyleSheet("font-size: 14px; padding: 10px 0px 10px 10px;")
        no_button.setStyleSheet("font-size: 14px; padding: 10px 10px 10px 0px;")
        
        radio_box_layout.addLayout(toggle_layout)
        self.input_fields["paid"] = toggle_layout
        
        # sum paid input
        sum_paid_input, input_field = create_Vbox(self.fields_config["sum_paid"][0], QLineEdit(), self.fields_config["sum_paid"][1])
        self.input_fields["sum_paid"] = input_field
        
        # person dropdown
        person_dropdown, input_field = create_Vbox(self.fields_config["owner"][0], self.create_person_dropdown())
        self.input_fields["owner"] = input_field

        # type dropdown
        type_dropdown = QComboBox()
        type_list = self.type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown.setPlaceholderText(self.fields_config["type"][1])
        type_dropdown.setCurrentIndex(-1)
        type_dropdown, input_field = create_Vbox(self.fields_config["type"][0], type_dropdown)
        self.input_fields["type"] = input_field

        # note input
        note_input, input_field = create_Vbox(self.fields_config["notes"][0], QLineEdit(), self.fields_config["notes"][1])
        self.input_fields["notes"] = input_field

        # stack everything together
        action_layout.addLayout(radio_box_layout)
        action_layout.addLayout(sum_paid_input)
        action_layout.addLayout(person_dropdown)
        action_layout.addLayout(type_dropdown)
        action_layout.addLayout(note_input)
        action_layout.setContentsMargins(0,0,0,0)
        
        vbox.addLayout(action_layout)
        
        return input_container
    
    def create_person_dropdown(self):
        person_dropdown = QComboBox()
        person_dropdown.setEditable(True)
        person_dropdown.setPlaceholderText(self.fields_config["owner"][1])
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

    def update_person_dropdown(self):
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
        
        self.load_data()

    def update_type_dropdown(self):
        type_dropdown:QComboBox = self.input_fields["type"]
        type_dropdown.clear()
        
        type_list = self.type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown.setPlaceholderText("Тип нерухомості")
        type_dropdown.setCurrentIndex(-1)

    def load_data(self):
        """Завантаження інформації з бази даних в таблицю"""
        self.table.clearSelection()
        self.table.clear_rows()
        records = self.estate_repo.get_all_record_by_year(self.window().get_current_year())
        
        [self.table.add_row(row) for row in records]

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
        
        # sum paid
        self.input_fields["sum_paid"].setText(row_data[8])
        
        # QComboBox ownner
        index = self.input_fields["owner"].findText(row_data[9])
        if index != -1:
            self.input_fields["owner"].setCurrentIndex(index)

        # QComboBox type
        type_name = row_data[10].split(" (")[0]
        index = self.input_fields["type"].findText(type_name)
        if index != -1:
            self.input_fields["type"].setCurrentIndex(index)
        
        self.input_fields["notes"].setText(row_data[11])

    def add_record(self):
        """Додавання запису"""
        data = [field for field in self.get_input_data().values()]

        if all(data[:-1]):
            try:
                float(data[2])
            except:
                QMessageBox.warning(self, "Помилка", "Значення площі повинно бути числом!")
                return
            try:
                float(data[4])
            except:
                QMessageBox.warning(self, "Помилка", "Значення сплати податку повинно бути числом!")
                return
            year = self.window().get_current_year()
            if not isinstance(data[-3], int):
                QMessageBox.warning(self, "Помилка", "Виберіть людину зі списку!")
                return
                
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
            try:
                float(data[4])
            except:
                QMessageBox.warning(self, "Помилка", "Значення сплати податку повинно бути числом!")
                return
            year = self.window().get_current_year()
            if not isinstance(data[-3], int):
                QMessageBox.warning(self, "Помилка", "Виберіть людину зі списку!")
                return
            
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
   