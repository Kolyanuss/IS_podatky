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
    class CustomSortFilterProxyModel(QSortFilterProxyModel):
        def __init__(self, filters, filter_columns_from_start, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.filters = filters
            self.filter_columns_from_start = filter_columns_from_start

        def filterAcceptsRow(self, source_row, source_parent):
            """
            Перевизначає метод для перевірки, чи повинен рядок залишатися у таблиці після фільтрації.
            """
            for column_index, text in self.filters.items():
                if text:  # Якщо фільтр для колонки встановлений
                    # Отримуємо дані з відповідної комірки
                    index = self.sourceModel().index(source_row, column_index, source_parent)
                    data = index.data(Qt.ItemDataRole.DisplayRole)
                    if not data:  # Пропускаємо, якщо дані порожні
                        return False
                    if column_index in self.filter_columns_from_start:
                        # Перевірка "від початку рядка"
                        if not str(data).lower().startswith(text.lower()):
                            return False
                    else:
                        # Перевірка наявності тексту у значенні
                        if text.lower() not in str(data).lower():
                            return False
            return True

    class ResizableTable(QTableView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Словник для зберігання поточного стану сортування для кожної колонки
            self.sort_states = {}
            # Підключаємо обробник кліку по заголовку
            self.horizontalHeader().sectionClicked.connect(self.handle_header_click)

        def handle_header_click(self, logical_index):
            # Отримуємо поточний стан сортування для колонки
            current_state = self.sort_states.get(logical_index, 0)
            
            # Очищаємо сортування для всіх колонок
            self.model().sort(-1, Qt.SortOrder.AscendingOrder)
            
            # Циклічно змінюємо стан (0 -> 1 -> 2 -> 0)
            # 0: без сортування
            # 1: за зростанням
            # 2: за спаданням
            new_state = (current_state + 1) % 3
            
            if new_state == 1:  # Сортування за зростанням
                self.model().sort(logical_index, Qt.SortOrder.AscendingOrder)
            elif new_state == 2:  # Сортування за спаданням
                self.model().sort(logical_index, Qt.SortOrder.DescendingOrder)
            # Якщо new_state == 0, сортування вже очищено
            
            # Зберігаємо новий стан
            self.sort_states[logical_index] = new_state

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

    def __init__(self, column_names, hiden_columns_id, cell_click_callback, filter_columns_from_start=None):
        """
        Створює віджет таблиці з фільтрацією за колонками.
        
        :param column_names: Список назв колонок
        :param cell_click_callback: Функція для обробки кліку по клітинці
        :param filter_columns_from_start: Список індексів колонок, які використовують фільтрацію "від початку"
        """
        super().__init__()

        self.column_names = column_names
        self.hiden_columns = hiden_columns_id
        self.filter_columns_from_start = filter_columns_from_start or []

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.column_names)

        self.filters = {}  # Словник для збереження тексту фільтрів для кожної колонки
        self.proxy_model = self.CustomSortFilterProxyModel(self.filters, self.filter_columns_from_start)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        # Дозволяємо сортування
        self.proxy_model.setSortRole(Qt.ItemDataRole.DisplayRole)
        self.proxy_model.setDynamicSortFilter(True)

        self.table = self.ResizableTable()
        self.table.setModel(self.proxy_model)
        
        for i in hiden_columns_id:
            self.table.setColumnHidden(i, True)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.clicked.connect(cell_click_callback)
        # Дозволяємо сортування для заголовків
        self.table.setSortingEnabled(True)
        apply_styles(self.table, ["table_view"])        

        self.filter_inputs = []
        filter_layout = QHBoxLayout()

        for i, column_name in enumerate(self.column_names):
            if i in hiden_columns_id:
                continue
            # Текстове поле для кожної колонки
            filter_input = QLineEdit()
            filter_input.setPlaceholderText(str(column_name).replace('\n',' '))
            filter_input.textChanged.connect(self.create_combined_filter_function(i))
            self.filter_inputs.append(filter_input)
            self.filters[i] = ""

            filter_layout.addWidget(filter_input)

        # Основний макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def create_combined_filter_function(self, column_index):
        """
        Створює функцію для комбінованої фільтрації за всіма колонками.

        :param column_index: Індекс колонки, яку потрібно фільтрувати
        """
        def update_filter(text):
            self.filters[column_index] = text
            self.proxy_model.invalidateFilter()
        return update_filter

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