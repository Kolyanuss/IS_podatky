from PyQt6.QtWidgets import (
    QPushButton, QMessageBox, QTableWidget, QHeaderView,
    QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from ui.styles import get_button_style, apply_styles

def create_button(text, button_type, callback):
    """Створення кнопки з заданими параметрами"""
    button = QPushButton(text)
    button.setStyleSheet(get_button_style(button_type))
    button.clicked.connect(callback)
    return button

def create_CUD_buttons(add_func, update_func, delete_func):
    """Створення панелі з кнопками"""
    button_layout = QHBoxLayout()
    
    add_button = create_button("Додати", "success", add_func)
    update_button = create_button("Оновити", "primary", update_func)
    delete_button = create_button("Видалити", "danger", delete_func)
    
    button_layout.addWidget(add_button)
    button_layout.addWidget(update_button)
    button_layout.addWidget(delete_button)
    button_layout.setSpacing(15)
    
    return button_layout

def confirm_delete():
    reply = QMessageBox()
    reply.setIcon(QMessageBox.Icon.Question)
    reply.setWindowTitle('Підтвердження')
    reply.setText('Ви впевнені, що хочете видалити цей запис?')
    reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    reply.button(QMessageBox.StandardButton.Yes).setText('Так, видалити')
    reply.button(QMessageBox.StandardButton.No).setText('Ні, скасувати')
    return reply.exec()

def create_table_widget(col_num, columns, conect_func):
    """Створення таблиці"""
    table = QTableWidget()
    table.setColumnCount(col_num)
    table.setHorizontalHeaderLabels(columns)
    table.setColumnHidden(0, True)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setAlternatingRowColors(True)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.cellClicked.connect(conect_func)
    apply_styles(table, ["table"])
    return table

def create_Vbox(lable_name:str, input_field):
    vbox = QVBoxLayout()
    label = QLabel(lable_name)
    
    vbox.addWidget(label)
    vbox.addWidget(input_field)
    return vbox, input_field