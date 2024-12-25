from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFrame, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QHeaderView
)
from ui.styles import apply_style, apply_styles, get_button_style

def create_button(text, button_type, callback):
    """Створення кнопки з заданими параметрами"""
    button = QPushButton(text)
    button.setStyleSheet(get_button_style(button_type))
    button.clicked.connect(callback)
    return button