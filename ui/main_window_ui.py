from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QFileDialog,
    QWidget, QMenuBar, QMenu, QLabel, QMessageBox, QStackedLayout, QApplication
)
from PyQt6.QtGui import QAction
import pandas as pd
from ui.add_person_ui import AddPersonDialog
from ui.styles import apply_styles, get_button_style
from ui.year_box import YearComboBox
from ui.min_salary_ui import MinSalaryDialog
from ui.change_estate_type_ui import EstateTypeDialog
from ui.change_land_type_ui import LandTypeDialog
from ui.real_estate_ui import RealEstateWidget
from ui.land_parcel_ui import LandParcelWidget
from ui.nmv_dialog import InputNMVDialog

from app.database import Database
from app.salary_repository import SalaryRepository
from app.real_estate_repository import RealEstateRepository
from app.land_parcel_repository import LandParcelRepository
from app.real_estate_type_repository import RealEstateTypeBaseRepository
from app.land_parcel_type_repository import LandParcelTypeBaseRepository
from app.user_repository import UserRepository

class MainWindow(QMainWindow):
    def __init__(self, db:Database):
        super().__init__()
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.estate_repo = RealEstateRepository(db)
        self.land_repo = LandParcelRepository(db)
        self.estate_type_base_repo = RealEstateTypeBaseRepository(db)
        self.land_type_base_repo = LandParcelTypeBaseRepository(db)
        
        QApplication.instance().aboutToQuit.connect(db.save_DB_backup)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("База оподаткування")
        self.setGeometry(100, 100, 1400, 700)

        apply_styles(self, ["base", "input_field", "label"])

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(3,3,3,3)

        top_button_layout = self.create_top_button_layout()

        self.stacked_layout = QStackedLayout()
        self.estate_widget = RealEstateWidget(self, self.db)
        self.land_widget = LandParcelWidget(self, self.db)
        self.stacked_layout.addWidget(self.estate_widget)
        self.stacked_layout.addWidget(self.land_widget)

        self.create_menu_bar()
        main_layout.addLayout(top_button_layout)
        main_layout.addLayout(self.stacked_layout)
        central_widget.setLayout(main_layout)
        
        self.combo_check()
    
    def change_table_action(self):
        self.change_type_button.clicked.disconnect()
        if self.stacked_layout.currentIndex() == 0:
            self.stacked_layout.setCurrentIndex(1)
            self.change_type_button.setText("Типи земельних ділянок")
            self.change_type_button.clicked.connect(self.open_change_land_type_dialog)
        else:
            self.stacked_layout.setCurrentIndex(0)
            self.change_type_button.setText("Типи нерухомості\nвідмінні від земельних ділянок")
            self.change_type_button.clicked.connect(self.open_change_estate_type_dialog)
        self.check_type_button()
        self.load_data()

    def create_menu_bar(self):
        """Створення меню бару"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Actions Menu
        actions_menu = QMenu("Дії", self)
        # import_action = QAction("Імпорт з Excel", self)
        export_action = QAction("Експорт в Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        restore_action = QAction("Відновити резервну копію бази даних", self)
        restore_action.triggered.connect(self.restore_db_backup_action)
        place_value_action = QAction("Вставити значення нормативно грошової оцінки як за попередній рік", self)
        place_value_action.triggered.connect(self.stacked_layout.widget(1).insert_nmv_from_last_year)
        change_value_action = QAction("Змінити всі значення нормативно грошової оцінки", self)
        change_value_action.triggered.connect(self.open_nmv_dialog)
        
        # actions_menu.addAction(import_action)
        actions_menu.addAction(export_action)
        actions_menu.addAction(restore_action)
        actions_menu.addAction(place_value_action)
        actions_menu.addAction(change_value_action)
        menu_bar.addMenu(actions_menu)

    def create_top_button_layout(self):
        """Створення лейауту з кнопками"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10,10,10,0)
        
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
        self.min_salary_button.clicked.connect(self.open_min_salary_dialog)

        # switch table
        switch_table_button = QPushButton("Змінити таблицю")
        switch_table_button.clicked.connect(self.change_table_action)
        switch_table_button.setStyleSheet(get_button_style("neutral") + """
                QPushButton {
                min-height: 60px;
            }""")

        # estate types
        self.change_type_button = QPushButton("Типи нерухомості\nвідмінні від земельних ділянок")
        self.change_type_button.clicked.connect(self.open_change_estate_type_dialog)

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

    def open_nmv_dialog(self):
        dialog = InputNMVDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.stacked_layout.widget(1).update_all_normative_monetary_values(dialog.value1, dialog.value2)
    
    def open_add_person_dialog(self):
        """Відкриття діалогу додавання користувача."""
        current_layout = self.stacked_layout.currentWidget()
        
        self.person_dialog = AddPersonDialog(self.db)
        self.person_dialog.edited_signal.connect(current_layout.update_person_dropdown)
        self.person_dialog.show()
        
    def open_min_salary_dialog(self):
        self.salary_window = MinSalaryDialog(self.db, self.get_current_year())
        self.salary_window.close_signal.connect(self.combo_check)
        self.salary_window.edited_signal.connect(self.update_all_estate_tax)
        self.salary_window.exec()
    
    def open_change_estate_type_dialog(self):
        estate_type_window = EstateTypeDialog(self.db, self.get_current_year())
        estate_type_window.close_signal.connect(self.combo_check)
        estate_type_window.edited_signal.connect(self.update_all_estate_tax)
        estate_type_window.add_update_delete_signal.connect(self.stacked_layout.currentWidget().update_type_dropdown)
        estate_type_window.update_table_signal.connect(self.load_data)
        estate_type_window.exec()
    
    def open_change_land_type_dialog(self):
        land_type_window = LandTypeDialog(self.db, self.get_current_year())
        land_type_window.close_signal.connect(self.combo_check)
        land_type_window.edited_signal.connect(self.update_all_land_tax)
        land_type_window.add_update_delete_signal.connect(self.stacked_layout.currentWidget().update_type_dropdown)
        land_type_window.update_table_signal.connect(self.load_data)
        land_type_window.exec()
    
    def update_all_estate_tax(self, type_record_id:int = None):
        try:
            self.estate_repo.update_all_tax(self.get_current_year(), type_record_id)
            QMessageBox.information(self, "Успіх!", "Нові податки було успішно розраховано!")
        except Exception as e:
            QMessageBox.warning(self, "Попередження!", f"Не вдалося розрахувати нові податки: {e}")
        self.load_data()
    
    def update_all_land_tax(self, type_record_id:int = None):
        try:
            self.land_repo.update_all_tax(self.get_current_year(), type_record_id)
            QMessageBox.information(self, "Успіх!", "Нові податки було успішно розраховано!")
        except Exception as e:
            QMessageBox.warning(self, "Попередження!", f"Не вдалося розрахувати нові податки: {e}")
        self.stacked_layout.widget(1).load_data()

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
            if self.stacked_layout.currentIndex() == 0: # if current type is real estate:
                records = self.estate_type_base_repo.get_type_rates(self.get_current_year())
            else: # else current type is land parcel:
                records = self.land_type_base_repo.get_type_rates(self.get_current_year())
                
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

    def restore_db_backup_action(self):
        """Обробка кнопки завантаження копії."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Виберіть резервну копію", self.db.backup_dir, "SQLite Files (*.db)")
        if file_path:
            if self.db.load_DB_backup(file_path):
                QMessageBox.information(self, "Успіх", "Базу даних успішно відновлено!")
                self.stacked_layout.currentWidget().load_data()
                self.combo_check()
            else:
                QMessageBox.critical(self, "Помилка", "Не вдалося відновити базу даних.")

    def export_to_excel(self):
        year = self.get_current_year()
        output_file = f"exported_data_{year}.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            user_repo = UserRepository(self.db)
            records = user_repo.get_all_record()
            df = pd.DataFrame(records, columns=["id","Прізвище","Ім'я","По батькові","Код платника податків","Адреса","Електронна пошта","Телефон"])
            df = df.drop("id", axis=1)
            df.to_excel(writer, sheet_name="Люди", index=False)
            
            records = self.estate_repo.get_all_record_by_year(year)
            estate_col_names = self.stacked_layout.widget(0).table_column
            df = pd.DataFrame(records, columns=estate_col_names)
            df = df.drop([estate_col_names[0],estate_col_names[1]], axis=1)
            df.to_excel(writer, sheet_name="Нерухомість", index=False)
            
            records = self.land_repo.get_all_record_by_year(year)
            land_col_names = self.stacked_layout.widget(1).table_column
            df = pd.DataFrame(records, columns=land_col_names)
            df = df.drop([land_col_names[0],land_col_names[1]], axis=1)
            df.to_excel(writer, sheet_name="Земельні ділянки", index=False)

        QMessageBox.information(self, "Успіх!", f"Дані успішно експортовані до файлу: {output_file}")
    