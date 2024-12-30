from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt
from datetime import datetime

class YearComboBox(QComboBox):
    def __init__(self):
        super().__init__()

        current_year = datetime.now().year
        years = range(current_year-30, current_year+5)
        self.addItems([str(year) for year in years])
        
        self.setCurrentText(str(current_year))
        
        self.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 3px 3px 3px 10px;
                max-width: 110px;
                font-size: 16px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox:hover {
                background-color: #3d3d3d;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                selection-background-color: #8d8484;
                selection-color: white;
                border: 1px solid #5f4747;
            }
        """)