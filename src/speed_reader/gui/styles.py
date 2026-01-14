"""
Modern color scheme and styles for Speed Reader.
"""
# Modern color palette - Dark theme with accent colors
COLORS = {
    'background': '#1e1e1e',
    'surface': '#2d2d2d',
    'surface_light': '#3d3d3d',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'text_muted': '#808080',
    'accent': '#4a9eff',
    'accent_hover': '#6bb0ff',
    'accent_light': '#7bbfff',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'border': '#404040',
    'border_light': '#505050',
    'highlight': '#ffff00',
    'highlight_bg': '#ffff0020',
}

# Light theme alternative
COLORS_LIGHT = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'surface_light': '#fafafa',
    'text_primary': '#212121',
    'text_secondary': '#616161',
    'text_muted': '#9e9e9e',
    'accent': '#2196f3',
    'accent_hover': '#42a5f5',
    'accent_light': '#64b5f6',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'border': '#e0e0e0',
    'border_light': '#f0f0f0',
    'highlight': '#ffeb3b',
    'highlight_bg': '#fff9c420',
}

def get_stylesheet(theme='dark'):
    """Get the complete stylesheet for the application."""
    colors = COLORS if theme == 'dark' else COLORS_LIGHT
    
    return f"""
    QMainWindow {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
    }}
    
    QWidget {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    QGroupBox {{
        font-weight: bold;
        font-size: 13px;
        border: 2px solid {colors['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 12px;
        background-color: {colors['surface']};
        color: {colors['text_primary']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {colors['accent']};
    }}
    
    QPushButton {{
        background-color: {colors['accent']};
        color: {colors['text_primary']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 500;
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {colors['accent_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {colors['accent']};
    }}
    
    QPushButton:disabled {{
        background-color: {colors['surface_light']};
        color: {colors['text_muted']};
    }}
    
    QLabel {{
        color: {colors['text_primary']};
        font-size: 12px;
    }}
    
    QSlider::groove:horizontal {{
        border: 1px solid {colors['border']};
        height: 6px;
        background: {colors['surface_light']};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {colors['accent']};
        border: 2px solid {colors['accent']};
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {colors['accent_hover']};
        border: 2px solid {colors['accent_hover']};
    }}
    
    QSpinBox {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 4px;
        padding: 4px;
        color: {colors['text_primary']};
        font-size: 12px;
    }}
    
    QSpinBox:hover {{
        border: 1px solid {colors['accent']};
    }}
    
    QSpinBox:focus {{
        border: 2px solid {colors['accent']};
    }}
    
    QComboBox {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 4px;
        padding: 6px;
        color: {colors['text_primary']};
        font-size: 12px;
        min-height: 24px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {colors['accent']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {colors['text_secondary']};
        width: 0;
        height: 0;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        selection-background-color: {colors['accent']};
        selection-color: {colors['text_primary']};
        color: {colors['text_primary']};
    }}
    
    QCheckBox {{
        color: {colors['text_primary']};
        font-size: 12px;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {colors['border']};
        border-radius: 4px;
        background-color: {colors['surface']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {colors['accent']};
        border-color: {colors['accent']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {colors['accent']};
    }}
    
    QTextEdit {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        padding: 8px;
        color: {colors['text_primary']};
        font-size: 12px;
        selection-background-color: {colors['accent']};
    }}
    
    QProgressBar {{
        border: 1px solid {colors['border']};
        border-radius: 4px;
        text-align: center;
        background-color: {colors['surface_light']};
        color: {colors['text_primary']};
        font-size: 11px;
        height: 20px;
    }}
    
    QProgressBar::chunk {{
        background-color: {colors['accent']};
        border-radius: 3px;
    }}
    """
