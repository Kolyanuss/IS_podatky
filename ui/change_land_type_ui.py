from PyQt6.QtWidgets import (
    QLineEdit, QVBoxLayout, QDialog,
    QMessageBox, QTableWidgetItem, QFrame, QHBoxLayout
)

from PyQt6.QtCore import pyqtSignal
from ui.styles import apply_style, apply_styles
from ui.utils import create_table_widget, create_CUD_buttons, create_Vbox, confirm_delete
from app.land_parcel_type_repository import LandParcelTypeBaseRepository, DeleteExeption
from app.database import Database


class LandTypeDialog(QDialog):
    close_signal = pyqtSignal()
    edited_signal = pyqtSignal()
    add_update_delete_signal = pyqtSignal()
    update_table_signal = pyqtSignal()
    def __init__(self, database:Database, year:int):
        super().__init__()
        self.land_type_repo = LandParcelTypeBaseRepository(database)
        self.year = year
        self.input_fields = {}
        self.fields_config = [
            ("type", "Тип", "Введіть назву типу*"),
            ("rate", "Ставка %", "Введіть ставку*"),
        ]
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Ініціалізація основного інтерфейсу"""
        self.setWindowTitle("Типи земельних ділянок та ставки (за попередній рік)")
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setFixedSize(600,400)
        
        apply_styles(self, ["base", "input_field", "label"])
        
        self.table = create_table_widget(len(self.fields_config)+1, ["id"]+[item[1] for item in self.fields_config], self.on_cell_click)
        
        input_container = self.create_input_container()
        
        button_layout = create_CUD_buttons(self.add_record, self.update_record, self.delete_record)
        
        # Компонування основного лейауту
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(input_container)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_input_container(self):
        """Створення контейнера з полями вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        apply_style(input_container, "input_container")
        
        input_grid = QHBoxLayout(input_container)
        input_grid.setSpacing(10)

        # Конфігурація полів вводу
        for field_name, label_text, placeholder in self.fields_config:
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            field_layout, input_field = create_Vbox(label_text, input_field)
            self.input_fields[field_name] = input_field
            input_grid.addLayout(field_layout)

        return input_container

    def load_data(self):
        """Завантаження інформації з бази даних"""
        self.table.clearSelection()
        try:
            records = self.land_type_repo.get_type_rates(self.year)
            self.table.setRowCount(len(records))
            for row_idx, row in enumerate(records):
                for col_idx, item in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити інформацію: {e}")
                
    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)
        
    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""        
        i = 1
        for field in self.input_fields.values():
            field.setText(self.table.item(row, i).text())
            i += 1
    
    def clear_inputs(self):
        """Очищення всіх полів введення."""
        self.table.clearSelection()
        for field in self.input_fields.values():
            field.clear()
            
    def add_record(self):
        """Додавання запису"""
        data = [field.text() for field in self.input_fields.values()]

        if all(data):
            try:
                float(data[1])
            except:
                QMessageBox.warning(self, "Помилка", "Ставка повинна бути числом!")
                return
            try:
                self.land_type_repo.add_record(self.year, *data)
                self.add_update_delete_signal.emit()
                # QMessageBox.information(self, "Успіх", "Тип нерухомості успішно додано!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося додати тип земельної ділянки: {e}")
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def update_record(self):
        """Оновлення запису"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для оновлення!")
            return
        
        record_id = self.table.item(selected_row, 0).text()
        data = [field.text() for field in self.input_fields.values()]

        if record_id and all(data):
            try:
                float(data[1])
            except:
                QMessageBox.warning(self, "Помилка", "Ставка повинна бути числом!")
                return
            try:
                self.land_type_repo.update_record(record_id, self.year, *data)
                self.edited_signal.emit()
                self.add_update_delete_signal.emit()
                # QMessageBox.information(self, "Успіх", "Тип нерухомості успішно оновлено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося оновити тип земельної ділянки: {e}")
            self.clear_inputs()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def delete_record(self):
        """Видалення запису"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення!")
            return
            
        record_id = self.table.item(selected_row, 0).text()
        type_name = self.table.item(selected_row, 1).text()
        
        if confirm_delete() == QMessageBox.StandardButton.Yes:
            try:
                self.land_type_repo.delete_record(record_id, type_name)
                self.add_update_delete_signal.emit()
                QMessageBox.information(self, "Успіх", "Тип земельної ділянки видалено!")
            except DeleteExeption as e:
                QMessageBox.warning(self, "Увага", f"Інформацію видалено частково: {e}")
                self.update_table_signal.emit()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити запис: {e}")

            self.clear_inputs()
            self.load_data()