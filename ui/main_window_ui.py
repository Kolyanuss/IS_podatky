import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QMenu, QLineEdit, QComboBox,
    QCompleter
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        action_layout = QHBoxLayout()

        # Menu Bar
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

        # Buttons (Top Row)
        year_button = QPushButton("YEAR\n2024")
        year_button.setStyleSheet("background-color: pink; font-size: 14px;")

        min_salary_button = QPushButton("Min salary")
        min_salary_button.setStyleSheet("background-color: lightgreen; font-size: 14px;")

        switch_table_button = QPushButton("Switch Table")
        switch_table_button.setStyleSheet("background-color: lightblue; font-size: 14px;")

        change_type_button = QPushButton("Change Type")
        change_type_button.setStyleSheet("background-color: lightyellow; font-size: 14px;")

        add_person_button = QPushButton("Add New Person")
        add_person_button.setStyleSheet("background-color: violet; font-size: 14px;")

        button_layout.addWidget(year_button)
        button_layout.addWidget(min_salary_button)
        button_layout.addWidget(switch_table_button)
        button_layout.addWidget(change_type_button)
        button_layout.addWidget(add_person_button)

        # Table
        self.table = QTableWidget(5, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Address", "Area", "Type", "Note"])
        self.table.setStyleSheet("font-size: 14px;")
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_layout.addWidget(self.table)

        # Bottom Controls
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

        name_input = QLineEdit()
        name_input.setPlaceholderText("Name")

        address_input = QLineEdit()
        address_input.setPlaceholderText("Address")

        area_input = QLineEdit()
        area_input.setPlaceholderText("Area")

        type_dropdown = QComboBox()
        type_dropdown.addItems(["Type 1", "Type 2", "Type 3"])

        note_input = QLineEdit()
        note_input.setPlaceholderText("Note")

        add_button = QPushButton("Add")
        update_button = QPushButton("Update")
        delete_button = QPushButton("Delete")

        action_layout.addWidget(person_dropdown)
        action_layout.addWidget(name_input)
        action_layout.addWidget(address_input)
        action_layout.addWidget(area_input)
        action_layout.addWidget(type_dropdown)
        action_layout.addWidget(note_input)
        action_layout.addWidget(add_button)
        action_layout.addWidget(update_button)
        action_layout.addWidget(delete_button)

        # Combine Layouts
        main_layout.addLayout(button_layout)
        main_layout.addLayout(table_layout)
        main_layout.addLayout(action_layout)
        central_widget.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
