from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFrame, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QHeaderView, QWidget
)
from PyQt6.QtCore import Qt
from ui.styles import apply_style, apply_styles
from ui.utils import confirm_delete, create_table_widget, create_CUD_buttons
from app.database import Database
from app.user_repository import UserRepository

class AddPersonDialog(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.user_repository = UserRepository(db)
        self.input_fields = {}
        self.fields_config = [
            ("last_name", "Прізвище", "Введіть прізвище*"),
            ("name", "Ім'я", "Введіть ім'я*"),
            ("middle_name", "По батькові", "Введіть по батькові*"),
            ("rnokpp", "РНОКПП", "Введіть РНОКПП*"),
            ("address", "Адреса", "Введіть адресу*"),
            ("email", "Email", "Введіть email"),
            ("phone", "Телефон", "Введіть телефон")
        ]
        
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """Ініціалізація основного інтерфейсу"""
        self.setWindowTitle("Список осіб")
        self.setGeometry(100, 100, 1200, 700)
        
        apply_styles(self, ["base", "input_field", "label"])
        
        self.table = create_table_widget(8, ["Id"]+[item[1] for item in self.fields_config], self.on_cell_click)
        input_container = self.create_input_container()
        button_layout = create_CUD_buttons(self.add_person, self.update_person, self.delete_record)
        
        # Компонування основного лейауту
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(input_container)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def create_input_field(self, label_text, placeholder):
        """Створення окремого поля вводу з міткою"""
        field_layout = QVBoxLayout()
        
        label = QLabel(label_text)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        
        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        
        return field_layout, input_field

    def create_input_container(self):
        """Створення контейнера з полями вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        apply_style(input_container, "input_container")
        
        input_grid = QHBoxLayout(input_container)
        input_grid.setSpacing(10)

        # Конфігурація полів вводу
        for field_name, label_text, placeholder in self.fields_config:
            field_layout, input_field = self.create_input_field(label_text, placeholder)
            self.input_fields[field_name] = input_field
            input_grid.addLayout(field_layout)

        return input_container

    def load_users(self):
        """Завантаження користувачів у таблицю."""
        users = self.user_repository.get_all_record()
        self.table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            for col_idx, data in enumerate(user):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    def add_person(self):
        """Додавання нового користувача в базу даних."""
        data = [field.text() for field in self.input_fields.values()]

        if all(data[:-2]):
            try:
                int(data[3])
            except:
                QMessageBox.warning(self, "Помилка", "Код платника податків повинен бути числом!")
                return
            try:
                self.user_repository.add_record(data)
                QMessageBox.information(self, "Успіх", "Користувача успішно додано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося додати користувача: {e}")
            self.clear_inputs()
            self.load_users()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def update_person(self):
        """Оновлення вибраного користувача."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для оновлення!")
            return
        
        record_id = self.table.item(selected_row, 0).text()
        data = [field.text() for field in self.input_fields.values()]

        if all(data[:-2]):
            try:
                int(data[3])
            except:
                QMessageBox.warning(self, "Помилка", "Код платника податків повинен бути числом!")
                return
            try:
                self.user_repository.update_record(record_id, data)
                QMessageBox.information(self, "Успіх", "Дані користувача оновлено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося оновити користувача: {e}")
            self.clear_inputs()
            self.load_users()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")


    def delete_record(self):
        """Видалення вибраного запису."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення!")
            return
            
        record_id = self.table.item(selected_row, 0).text()
        
        if confirm_delete() == QMessageBox.StandardButton.Yes:
            try:
                self.user_repository.delete_record(record_id)
                QMessageBox.information(self, "Успіх", "Користувача видалено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити користувача: {e}")
            self.clear_inputs()
            self.load_users()
        

    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""        
        i = 1
        for field in self.input_fields.values():
            field.setText(self.table.item(row, i).text())
            i += 1

    def clear_inputs(self):
        """Очищення всіх полів введення."""
        for field in self.input_fields.values():
            field.clear()
