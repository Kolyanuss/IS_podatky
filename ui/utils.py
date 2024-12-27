from PyQt6.QtWidgets import (
    QPushButton, QMessageBox
)
from ui.styles import get_button_style

def create_button(text, button_type, callback):
    """Створення кнопки з заданими параметрами"""
    button = QPushButton(text)
    button.setStyleSheet(get_button_style(button_type))
    button.clicked.connect(callback)
    return button

def confirm_delete():
    reply = QMessageBox()
    reply.setIcon(QMessageBox.Icon.Question)
    reply.setWindowTitle('Підтвердження')
    reply.setText('Ви впевнені, що хочете видалити цей запис?')
    reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    reply.button(QMessageBox.StandardButton.Yes).setText('Так, видалити')
    reply.button(QMessageBox.StandardButton.No).setText('Ні, скасувати')
    return reply.exec()