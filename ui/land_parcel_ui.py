from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QWidget,
    QCompleter, QFrame, QLabel, QRadioButton, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt

from ui.styles import apply_style
from ui.utils import create_CUD_buttons, create_Vbox, confirm_delete
from ui.filterable_table_view import FilterableTableWidget

from app.land_parcel_repository import LandParcelRepository, NormativeMonetaryValuesRepository
from app.land_parcel_type_repository import LandParcelTypeRepository
from app.user_repository import UserRepository

class LandParcelWidget(QWidget):
    def __init__(self, parent, db):
        super().__init__(parent=parent)
        
        self.input_fields = {}
        self.db = db
        self.land_repo = LandParcelRepository(db)
        self.land_type_repo = LandParcelTypeRepository(db)
        self.user_repo = UserRepository(db)
        self.normative_monetary_value_repo = NormativeMonetaryValuesRepository(db)
        self.input_fields = {}
        self.fields_config = [
            # ("name", "Назва земельної ділянки", "Введіть назву*"),
            ("address", "Урочище, Адреса\nземельної ділянки", "Введіть адресу*"),
            ("area", "Площа\nм^2", "Введіть площу*"),
            ("privileged", "Пільговик", ""),
            ("normative_monetary_value", "Нормативно\nгрошова оцінка", "Введіть грошову оцінку*"),
            ("tax", "Податок\n(грн)", ""),
            ("paid", "Сплачено", ""),
            ("owner", "Власник ділянки", "Виберіть власника*"),
            ("type", "Тип ділянки", "Виберіть тип*"),
            ("notes", "Нотатки", "Ваші нотатки"),
        ]
        self.table_column = ["id", "person_id"] + [row[1] for row in self.fields_config]
        
        
        self.init_ui()
        self.load_data()
        self.table.proxy_model.sort(-1, Qt.SortOrder.AscendingOrder)
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        self.table = FilterableTableWidget(self.table_column, [0,1], self.on_cell_click, [3,5,6])
        for i in [4,5,6,7,8]:
            self.table.table.horizontalHeader().resizeSection(i,75)
            
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
        
        action_layout = QHBoxLayout(input_container)
        
        # address area
        for field_name, label_text, placeholder in self.fields_config[:2]: 
            field_layout, input_field = create_Vbox(label_text, QLineEdit(), placeholder)
            self.input_fields[field_name] = input_field
            action_layout.addLayout(field_layout)
            
        self.input_fields["area"].setMaximumWidth(120)

        # privileged radio button (група 1)
        privileged_layout = QVBoxLayout()
        privileged_layout.addWidget(QLabel(self.fields_config[2][1]))
        
        toggle_layout1 = QHBoxLayout()
        yes_button1 = QRadioButton("Так")
        no_button1 = QRadioButton("Ні")
        no_button1.setChecked(True)  # За замовчуванням вибрано "Ні"
        toggle_layout1.addWidget(yes_button1)
        toggle_layout1.addWidget(no_button1)
        yes_button1.setStyleSheet("font-size: 14px; padding: 10px 0px 10px 10px;")
        no_button1.setStyleSheet("font-size: 14px; padding: 10px 10px 10px 0px;")
        
        # Додаємо кнопки до групи 1
        self.privileged_group = QButtonGroup()
        self.privileged_group.addButton(yes_button1)
        self.privileged_group.addButton(no_button1)
        
        privileged_layout.addLayout(toggle_layout1)
        self.input_fields[self.fields_config[2][0]] = toggle_layout1

        # normative_monetary_value input
        normative_monetary_value_input, input_field = create_Vbox(self.fields_config[3][1], QLineEdit(), self.fields_config[3][2])
        self.input_fields[self.fields_config[3][0]] = input_field
        
        # paid radio button (група 2)
        radio_box_layout = QVBoxLayout()
        radio_box_layout.addWidget(QLabel(self.fields_config[5][1]))
        
        toggle_layout2 = QHBoxLayout()
        yes_button2 = QRadioButton("Так")
        no_button2 = QRadioButton("Ні")
        no_button2.setChecked(True)  # За замовчуванням вибрано "Ні"
        toggle_layout2.addWidget(yes_button2)
        toggle_layout2.addWidget(no_button2)
        yes_button2.setStyleSheet("font-size: 14px; padding: 10px 0px 10px 10px;")
        no_button2.setStyleSheet("font-size: 14px; padding: 10px 10px 10px 0px;")
        
        # Додаємо кнопки до групи 2
        self.paid_group = QButtonGroup()
        self.paid_group.addButton(yes_button2)
        self.paid_group.addButton(no_button2)
        
        radio_box_layout.addLayout(toggle_layout2)
        self.input_fields[self.fields_config[5][0]] = toggle_layout2
        
        # person dropdown
        person_dropdown, input_field = create_Vbox(self.fields_config[-3][1], self.create_person_dropdown())
        self.input_fields[self.fields_config[-3][0]] = input_field

        # type dropdown
        type_dropdown = QComboBox()
        type_list = self.land_type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown.setPlaceholderText(self.fields_config[-2][2])
        type_dropdown.setCurrentIndex(-1)
        type_dropdown, input_field = create_Vbox(self.fields_config[-2][1], type_dropdown)
        self.input_fields[self.fields_config[-2][0]] = input_field

        # note input
        note_input, input_field = create_Vbox(self.fields_config[-1][1], QLineEdit(), self.fields_config[-1][2])
        self.input_fields[self.fields_config[-1][0]] = input_field

        # stack everything together
        action_layout.addLayout(privileged_layout)
        action_layout.addLayout(normative_monetary_value_input)
        action_layout.addLayout(radio_box_layout)
        action_layout.addLayout(person_dropdown)
        action_layout.addLayout(type_dropdown)
        action_layout.addLayout(note_input)

        return input_container

    
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
        
        type_list = self.land_type_repo.get_all_record()
        type_dropdown.addItems([row[1] for row in type_list])
        type_dropdown.setPlaceholderText(self.fields_config[-2][2])
        type_dropdown.setCurrentIndex(-1)
    
    def load_data(self):
        """Завантаження інформації з бази даних в таблицю"""
        self.table.clearSelection()
        self.table.clear_rows()
        records = self.land_repo.get_all_record_by_year(self.window().get_current_year())
        
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
        
        # self.input_fields["name"].setText(row_data[2])
        self.input_fields["address"].setText(row_data[2])
        self.input_fields["area"].setText(row_data[3])
        
        # для QRadioButton (privileged)
        for j in range(self.input_fields["privileged"].count()):
            widget = self.input_fields["privileged"].itemAt(j).widget()
            if isinstance(widget, QRadioButton) and widget.text() == row_data[4]:
                widget.setChecked(True)
                break
        
        # normative_monetary_value
        self.input_fields["normative_monetary_value"].setText(row_data[5])
        
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

    def add_record(self):
        """Додавання запису"""
        data = [field for field in self.get_input_data().values()]

        if all(data[:-1]):
            try:
                float(data[1])
                float(data[3])
            except:
                QMessageBox.warning(self, "Помилка", "Значення площі та нормативно грошової оцінки повинно бути числом!")
                return
            year = self.window().get_current_year()
            try:
                self.land_repo.add_record(year, *data)
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
                float(data[1])
                float(data[3])
            except:
                QMessageBox.warning(self, "Помилка", "Значення площі та нормативно грошової оцінки повинно бути числом!")
                return
            year = self.window().get_current_year()
            try:
                self.land_repo.update_record(record_id, year, *data)
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
                self.land_repo.delete_record(record_id)
                QMessageBox.information(self, "Успіх", "Земельну ділянку видалено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити інформацію про земельну ділянку: {e}")
            self.clear_inputs()
            self.load_data()

    def update_all_normative_monetary_values(self, old_value, new_value):
        year = self.window().get_current_year()
        self.normative_monetary_value_repo.replace_values(year, old_value, new_value)
        self.window().update_all_land_tax() # load inside 
        # self.load_data()
    
    def insert_nmv_from_last_year(self):
        try:
            land_ids = [record[0] for record in self.land_repo.get_all_ids()]
            current_year = self.window().get_current_year()
            skiped_value = 0
            not_finded_value = 0
            completed_values = 0
            for id in land_ids:
                nmv_record = self.normative_monetary_value_repo.get_by_id_and_year(id, current_year)
                if not nmv_record: # якщо значення немає - копіюємо за попередній рік
                    old_normative_monetary_value = self.normative_monetary_value_repo.get_latest_value_by_id_and_year(id, current_year)
                    if old_normative_monetary_value is not None:
                        self.normative_monetary_value_repo.add_record((id, current_year, old_normative_monetary_value))
                        completed_values += 1
                    else:
                        not_finded_value += 1
                else:
                    skiped_value += 1
            QMessageBox.information(self, "Успіх!", f"Оновлення нормативно грошових оцінок завершено!\n Оновлено {completed_values} записів.\n Пропущено {skiped_value} заповнених значень.\n Пропущено {not_finded_value} не знайдених значень.")
            self.window().update_all_land_tax() # load inside 
            # self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка!", f"Помилка при копіюванні нормативно грошових оцінок! {e}")