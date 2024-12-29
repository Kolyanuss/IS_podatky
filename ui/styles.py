def get_global_styles():
    """Повертає словник з глобальними стилями для різних компонентів"""
    return {
        "base": """
            QWidget {
                font-family: 'Segoe UI', sans-serif;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f0efed;
                gridline-color: #dcdde1;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                selection-background-color: #92c9ff;
                selection-color: black;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QHeaderView::section:horizontal {
                background-color: #f5f6fa;
                padding: 5px;
                font-weight: bold;
            }            
            QHeaderView::section:vertical {
                background-color: #f5f6fa;
                padding: 5px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #dcdde1;
                border-right: 1px solid #dcdde1;
            }
        """,
        
        "input_field": """
            QLineEdit {
                padding: 5px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #92c9ff;
            }
            QComboBox {
                padding: 5px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
        """,
        
        "input_container":"""
            #inputContainer {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #dcdde1;
            }
        """,
        
        "label": """
            QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0px 5px 0px 5px;
                }
        """
        
    }

def apply_style(widget, style_name):
    """Застосовує конкретний стиль до віджета"""
    styles = get_global_styles()
    if style_name in styles:
        widget.setStyleSheet(styles[style_name])

def apply_styles(widget, style_names):
    """Застосовує декілька стилів до віджета"""
    styles = get_global_styles()
    combined_style = ""
    for style_name in style_names:
        if style_name in styles:
            combined_style += styles[style_name]
    widget.setStyleSheet(combined_style)

# Додаткові функції для кольорів кнопок
def get_button_colors():
    """Повертає словник з кольорами для різних типів кнопок"""
    return {
        "primary": {
            "base": "#3498db",
            "hover": "#2980b9"
        },
        "success": {
            "base": "#2ab664",
            "hover": "#0c9b48"
        },
        "danger": {
            "base": "#ec5342",
            "hover": "#96261a"
        },
        "warning": {
            "base": "#f1c40f",
            "hover": "#f39c12"
        },
        "neutral": {
            "base": "#c5c5c5",
            "hover": "#b2b2b2"
        }
    }

def get_button_style(button_type="primary"):
    """Повертає стиль для конкретного типу кнопки"""
    colors = get_button_colors()
    color_set = colors.get(button_type, colors["primary"])
    
    return f"""
        QPushButton {{
            background-color: {color_set["base"]};
            padding: 5px 10px;
            border-radius: 5px;
            border: none;
            color: #404040;
            font-weight: bold;
            font-size: 20px;
            margin: 1px;
        }}
        QPushButton:hover {{
            background-color: {color_set["hover"]};
            margin: 0px;
            border: 1px solid #636e72;
        }}
        QPushButton:pressed {{
            margin: 2px 0px 0px 2px;
            background-color: {color_set["base"]};
        }}
    """