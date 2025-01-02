from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QTableView,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from ui.styles import apply_styles


class FilterableTableWidget(QWidget):
    class ResizableTable(QTableView):
        def resizeEvent(self, event):
            super().resizeEvent(event)  # Викликаємо оригінальний метод обробки події
            self.resize_columns()  # Викликаємо нашу функцію для розтягування колонок

        def resize_columns(self):
            total_width = self.viewport().width()  # Отримуємо доступну ширину таблиці
            current_widths = [self.columnWidth(i) for i in range(self.model().columnCount())]  # Поточні ширини колонок
            total_current_width = sum(current_widths)  # Загальна ширина всіх колонок
            if total_current_width > 0:
                scale_factor = total_width / total_current_width  # Фактор масштабування
                for i in range(self.model().columnCount()):
                    self.setColumnWidth(i, int(current_widths[i] * scale_factor))

    def __init__(self, column_names, cell_click_callback):
        """
        Створює віджет таблиці з фільтрацією за колонками.
        
        :param column_names: Список назв колонок
        :param cell_click_callback: Функція для обробки кліку по клітинці
        """
        super().__init__()

        self.column_names = column_names

        # Модель даних
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.column_names)

        # Проксі-модель для фільтрації
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # Таблиця
        self.table = self.ResizableTable()
        self.table.setModel(self.proxy_model)
        
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(1, True)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setMinimumSectionSize(60)
        for i in [4,5,6,7]:
            self.table.horizontalHeader().resizeSection(i,75)
        
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.clicked.connect(cell_click_callback)  # З'єднання події кліку з переданою функцією
        apply_styles(self.table, ["table_view"])        
        # Поля для фільтрації
        self.filter_inputs = []
        filter_layout = QHBoxLayout()

        for i, column_name in enumerate(self.column_names[2:], 2):
            # Текстове поле для кожної колонки
            filter_input = QLineEdit()
            filter_input.setPlaceholderText(f"Пошук в {column_name}")
            filter_input.textChanged.connect(self.create_filter_function(i))  # Підключення фільтрації до колонки
            self.filter_inputs.append(filter_input)

            filter_layout.addWidget(filter_input)

        # Основний макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def create_filter_function(self, column_index):
        """
        Створює функцію для фільтрації конкретної колонки.
        
        :param column_index: Індекс колонки, яку потрібно фільтрувати
        """
        def filter_column(text):
            self.proxy_model.setFilterKeyColumn(column_index)
            self.proxy_model.setFilterFixedString(text)
        
        return filter_column

    def add_row(self, row_data):
        """
        Додає рядок у таблицю.
        
        :param row_data: Список значень для кожної колонки
        """
        items = [QStandardItem(str(value)) for value in row_data]
        self.model.appendRow(items)

    def clear_rows(self):
        """Очищає всі рядки таблиці."""
        self.model.removeRows(0, self.model.rowCount())
        
    def clearSelection(self):
        self.table.clearSelection()
        
    def get_row_values_by_index(self, index):
        # Отримання всіх значень з рядка index
        row_values = []
        for column in range(self.table.model().columnCount()):
            value = self.table.model().index(index, column).data()
            row_values.append(value)
        return row_values
    
    def get_current_row_index(self)->int:
        return self.table.currentIndex().row()
