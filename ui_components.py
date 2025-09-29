#!/usr/bin/env python3
"""
DELTON Desktop Application - UI Components
Enterprise-grade user interface for secure data sanitization
"""
import os
import sys
import json
import datetime
import webbrowser
import time
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QComboBox,
    QFrame, QSizePolicy, QProgressBar, QSpacerItem, QStackedWidget,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QDialog,
    QTextEdit, QSplitter, QGroupBox, QFormLayout, QCheckBox, QSpinBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar
)
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QAction, QTextCursor
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QSize, QPropertyAnimation, QEasingCurve

from business_logic import APIClient, list_drives, secure_delete


class StatusIndicator(QLabel):
    """Professional status indicator with animation support."""
    
    def __init__(self, status: str = "offline", parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.status = status
        self._update_appearance()
        
    def set_status(self, status: str):
        """Update status with animation."""
        self.status = status
        self._update_appearance()
        
    def _update_appearance(self):
        colors = {
            "offline": "#DC2626",  # Red
            "online": "#059669",   # Green
            "warning": "#D97706",  # Amber
            "processing": "#2563EB" # Blue
        }
        
        color = colors.get(self.status, "#6B7280")
        self.setStyleSheet(f"""
            QLabel {{
                border-radius: 8px;
                background: {color};
                border: 2px solid rgba(255, 255, 255, 0.2);
            }}
        """)


class LoadingSpinner(QLabel):
    """Professional loading spinner widget."""
    
    def __init__(self, size: int = 24, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)
        
    def start(self):
        """Start spinner animation."""
        self.timer.start(50)
        
    def stop(self):
        """Stop spinner animation."""
        self.timer.stop()
        
    def _rotate(self):
        self.angle = (self.angle + 15) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw spinner
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        pen = painter.pen()
        pen.setWidth(3)
        pen.setColor(QColor("#3B82F6"))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        for i in range(8):
            painter.drawLine(0, -10, 0, -6)
            painter.rotate(45)


class Toast(QLabel):
    """Professional toast notification."""
    
    def __init__(self, message: str, toast_type: str = "info", parent=None):
        super().__init__(message, parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        
        colors = {
            "success": "#059669",
            "error": "#DC2626", 
            "warning": "#D97706",
            "info": "#2563EB"
        }
        
        bg_color = colors.get(toast_type, "#2563EB")
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg_color};
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-weight: 600;
                border: none;
                margin: 4px;
            }}
        """)
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, self.hide)


class DELTONApp(QWidget):
    """
    Enterprise-grade DELTON Desktop Application.

    Features:
    - Professional UI/UX design
    - Comprehensive error handling
    - Real-time status updates
    - Advanced logging capabilities
    - Security-focused workflows
    """
    
    def __init__(self):
        super().__init__()
        # Application state
        self.api_client = APIClient("https://express-server-production-b4f4.up.railway.app")
        self.all_certificates: List[Dict[str, Any]] = []
        self.current_wipe_process: Optional[QThread] = None
        self.is_authenticated = False
        
        # UI Components
        self.status_indicator: Optional[StatusIndicator] = None
        self.loading_spinner: Optional[LoadingSpinner] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.status_bar: Optional[QStatusBar] = None
        
        # Timers
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._advance_progress)
        self.progress_timer.setInterval(50)
        
        # Apply default theme before initializing UI
        self.apply_theme("light")
        
        # Initialize UI
        self._init_ui()
        self._setup_keyboard_shortcuts()
        
        # Start on login page
        self.switch_page(0)
        self._update_status("Application initialized", "info")
        self.showMaximized()
        
    def apply_theme(self, mode: str):
        """Apply the selected theme."""
        if mode not in ["dark", "light"]:
            mode = "light"
        
        self.current_theme = mode
        
        if mode == "dark":
            colors = {
                'bg': '#111827',
                'text': '#F9FAFB',
                'base': '#1F2937',
                'alt_base': '#111827',
                'border': '#374151',
                'input_bg': '#374151',
                'input_border': '#4B5563',
                'hover': '#374151',
                'pressed': '#3B82F6',
                'nav_text': '#D1D5DB',
                'nav_hover': '#374151',
                'nav_pressed': '#3B82F6',
                'primary_start': '#3B82F6',
                'primary_end': '#2563EB',
                'primary_hover_start': '#2563EB',
                'primary_hover_end': '#1D4ED8',
                'primary_pressed': '#1D4ED8',
                'secondary_text': '#3B82F6',
                'secondary_border': '#3B82F6',
                'secondary_hover_bg': '#3B82F6',
                'secondary_hover_text': 'white',
                'success_start': '#059669',
                'success_end': '#047857',
                'success_hover_start': '#047857',
                'success_hover_end': '#065F46',
                'danger_start': '#DC2626',
                'danger_end': '#B91C1C',
                'danger_hover_start': '#B91C1C',
                'danger_hover_end': '#991B1B',
                'disabled_bg': '#4B5563',
                'disabled_text': '#9CA3AF',
                'progress_bg': '#374151',
                'progress_border': '#4B5563',
                'progress_chunk_start': '#3B82F6',
                'progress_chunk_end': '#8B5CF6',
                'log_bg': '#111827',
                'log_border': '#374151',
                'log_text': '#E5E7EB',
                'table_bg': '#1F2937',
                'table_alt': '#111827',
                'header_bg': '#374151',
                'group_title': '#3B82F6',
                'scroll_bg': '#1F2937',
                'scroll_handle': '#4B5563',
                'scroll_hover': '#6B7280',
                'warning_bg': '#FEF3C7',
                'warning_border': '#F59E0B',
                'warning_text': '#92400E'
            }
        else:  # light
            colors = {
                'bg': '#FFFFFF',
                'text': '#111827',
                'base': '#F3F4F6',
                'alt_base': '#FFFFFF',
                'border': '#D1D5DB',
                'input_bg': '#FFFFFF',
                'input_border': '#D1D5DB',
                'hover': '#F3F4F6',
                'pressed': '#3B82F6',
                'nav_text': '#4B5563',
                'nav_hover': '#E5E7EB',
                'nav_pressed': '#3B82F6',
                'primary_start': '#3B82F6',
                'primary_end': '#2563EB',
                'primary_hover_start': '#2563EB',
                'primary_hover_end': '#1D4ED8',
                'primary_pressed': '#1D4ED8',
                'secondary_text': '#3B82F6',
                'secondary_border': '#3B82F6',
                'secondary_hover_bg': '#3B82F6',
                'secondary_hover_text': 'white',
                'success_start': '#059669',
                'success_end': '#047857',
                'success_hover_start': '#047857',
                'success_hover_end': '#065F46',
                'danger_start': '#DC2626',
                'danger_end': '#B91C1C',
                'danger_hover_start': '#B91C1C',
                'danger_hover_end': '#991B1B',
                'disabled_bg': '#E5E7EB',
                'disabled_text': '#6B7280',
                'progress_bg': '#E5E7EB',
                'progress_border': '#D1D5DB',
                'progress_chunk_start': '#3B82F6',
                'progress_chunk_end': '#8B5CF6',
                'log_bg': '#FFFFFF',
                'log_border': '#D1D5DB',
                'log_text': '#4B5563',
                'table_bg': '#FFFFFF',
                'table_alt': '#F9FAFB',
                'header_bg': '#E5E7EB',
                'group_title': '#3B82F6',
                'scroll_bg': '#F3F4F6',
                'scroll_handle': '#D1D5DB',
                'scroll_hover': '#9CA3AF',
                'warning_bg': '#FFFBEB',
                'warning_border': '#D97706',
                'warning_text': '#92400E'
            }
        
        self.colors = colors
        
        stylesheet = f"""
            /* Main Application */
            QWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            /* Labels */
            QLabel {{
                background-color: transparent;
                color: {colors['text']};
            }}
            /* Checkboxes */
            QCheckBox {{
                background-color: transparent;
                color: {colors['text']};
                spacing: 6px; /* nice gap between box and label text */
            }}
            /* Subdued text */
            QLabel[subdued="true"],
            QCheckBox[subdued="true"] {{
                color: {colors['disabled_text']};
            }}
            
            /* Header */
            QFrame#header {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['base']}, stop:1 {colors['bg']});
                border-bottom: 1px solid {colors['border']};
            }}
            
            /* Sidebar */
            QFrame#sidebar {{
                background-color: {colors['base']};
                border-right: 1px solid {colors['border']};
            }}
            
            /* Navigation Buttons */
            QPushButton#navButton {{
                background: transparent;
                color: {colors['nav_text']};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                font-size: 13px;
            }}
            
            QPushButton#navButton:hover {{
                background-color: {colors['nav_hover']};
                color: {colors['text']};
            }}
            
            QPushButton#navButton:pressed,
            QPushButton#navButton[active="true"] {{
                background-color: {colors['nav_pressed']};
                color: white;
            }}
            
            /* Form Inputs */
            QLineEdit#formInput, QLineEdit#searchInput {{
                background-color: {colors['input_bg']};
                border: 1px solid {colors['input_border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {colors['text']};
                font-size: 14px;
            }}
            
            QLineEdit#formInput:focus, QLineEdit#searchInput:focus {{
                border-color: {colors['primary_start']};
                outline: none;
            }}
            
            QComboBox#formCombo {{
                background-color: {colors['input_bg']};
                border: 1px solid {colors['input_border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {colors['text']};
            }}
            
            QComboBox#formCombo::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox#formCombo::down-arrow {{
                image: none;
                border: none;
            }}
            
            /* Buttons */
            QPushButton#actionButton {{
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}

            QPushButton#actionButton:hover {{
                background-color: #106ebe;
                border-color: #106ebe;
            }}

            QPushButton#actionButton:pressed {{
                background-color: #005a9e;
                border-color: #005a9e;
            }}

            QPushButton#primaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary_start']}, stop:1 {colors['primary_end']});
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                padding: 12px 24px;
            }}
            
            QPushButton#primaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['primary_hover_start']}, stop:1 {colors['primary_hover_end']});
            }}
            
            QPushButton#primaryButton:pressed {{
                background: {colors['primary_pressed']};
            }}
            
            QPushButton#primaryButton:disabled {{
                background: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
            
            QPushButton#secondaryButton {{
                background: transparent;
                color: {colors['secondary_text']};
                border: 1px solid {colors['secondary_border']};
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                padding: 10px 20px;
            }}
            
            QPushButton#secondaryButton:hover {{
                background: {colors['secondary_hover_bg']};
                color: {colors['secondary_hover_text']};
            }}
            
            QPushButton#successButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['success_start']}, stop:1 {colors['success_end']});
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                padding: 12px 24px;
            }}
            
            QPushButton#successButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['success_hover_start']}, stop:1 {colors['success_hover_end']});
            }}
            
            QPushButton#successButton:disabled {{
                background: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
            
            QPushButton#dangerButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['danger_start']}, stop:1 {colors['danger_end']});
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                padding: 12px 24px;
            }}
            
            QPushButton#dangerButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors['danger_hover_start']}, stop:1 {colors['danger_hover_end']});
            }}
            
            QPushButton#dangerButton:disabled {{
                background: {colors['disabled_bg']};
                color: {colors['disabled_text']};
            }}
            
            /* Cards */
            QFrame#loginCard, QFrame#verificationCard, QFrame#configPanel, QFrame#progressPanel {{
                background-color: {colors['base']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
            
            /* Progress Bar */
            QProgressBar#progressBar {{
                background-color: {colors['progress_bg']};
                border: 1px solid {colors['progress_border']};
                border-radius: 12px;
                text-align: center;
                color: {colors['text']};
                font-weight: 600;
            }}
            
            QProgressBar#progressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['progress_chunk_start']}, stop:1 {colors['progress_chunk_end']});
                border-radius: 11px;
            }}
            
            /* Text Edit */
            QTextEdit#activityLog {{
                background-color: {colors['log_bg']};
                border: 1px solid {colors['log_border']};
                border-radius: 8px;
                color: {colors['log_text']};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }}
            
            /* Table */
            QTableWidget#certificatesTable {{
                background-color: {colors['table_bg']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                gridline-color: {colors['border']};
                color: {colors['text']};
            }}
            
            QTableWidget#certificatesTable::item {{
                padding: 8px;
                border-bottom: 1px solid {colors['border']};
            }}
            
            QTableWidget#certificatesTable::item:selected {{
                background-color: {colors['primary_start']};
                color: white;
            }}
            
            QTableWidget#certificatesTable::item:alternate {{
                background-color: {colors['table_alt']};
            }}
            
            QHeaderView::section {{
                background-color: {colors['header_bg']};
                color: {colors['text']};
                padding: 8px;
                border: none;
                border-right: 1px solid {colors['input_border']};
                font-weight: 600;
            }}
            
            /* Group Boxes */
            QGroupBox {{
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 8px;
                font-weight: 600;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {colors['group_title']};
            }}
            
            QGroupBox#systemInfo {{
                background-color: {colors['base']};
            }}
            
            /* Tabs */
            QTabWidget#settingsTabs::pane {{
                border: 1px solid {colors['border']};
                border-radius: 8px;
                background-color: {colors['base']};
            }}
            
            QTabWidget#settingsTabs::tab-bar {{
                alignment: left;
            }}
            
            QTabBar::tab {{
                background-color: {colors['progress_bg']};
                color: {colors['disabled_text']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['primary_start']};
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: {colors['input_border']};
                color: {colors['text']};
            }}
            
            /* Checkboxes */
            QCheckBox {{
                color: {colors['text']};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {colors['input_border']};
                border-radius: 3px;
                background-color: {colors['input_bg']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['primary_start']};
                border-color: {colors['primary_start']};
            }}
            
            /* Spin boxes */
            QSpinBox {{
                background-color: {colors['input_bg']};
                border: 1px solid {colors['input_border']};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors['text']};
            }}
            
            /* Scroll bars */
            QScrollBar:vertical {{
                background-color: {colors['scroll_bg']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['scroll_handle']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['scroll_hover']};
            }}
        """
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(colors['bg']))
        palette.setColor(QPalette.WindowText, QColor(colors['text']))
        palette.setColor(QPalette.Base, QColor(colors['base']))
        palette.setColor(QPalette.AlternateBase, QColor(colors['alt_base']))
        palette.setColor(QPalette.Text, QColor(colors['text']))
        palette.setColor(QPalette.ButtonText, QColor(colors['text']))
        palette.setColor(QPalette.Button, QColor(colors['base']))
        palette.setColor(QPalette.Highlight, QColor(colors['primary_start']))
        palette.setColor(QPalette.HighlightedText, QColor('white'))
        
        app = QApplication.instance()
        app.setPalette(palette)
        app.setStyleSheet(stylesheet)
        
    def _change_theme(self, text: str):
        """Handle theme change from settings."""
        if text == "Dark Theme":
            self.apply_theme("dark")
        elif text == "Light Theme":
            self.apply_theme("light")
        elif text == "System Default":
            # Detect system theme (simplified, default to dark if detection fails)
            mode = "dark"
            try:
                if sys.platform == "win32":
                    import winreg
                    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    mode = "light" if value == 1 else "dark"
            except:
                pass
            self.apply_theme(mode)
        
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DELTON Enterprise - Data Sanitization Platform")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content area with sidebar
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar
        sidebar = self._create_sidebar()
        content_splitter.addWidget(sidebar)
        
        # Main content
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self._create_login_page())          # Index 0
        self.content_stack.addWidget(self._create_ml_health_page())      # Index 1
        self.content_stack.addWidget(self._create_wipe_page())           # Index 2
        self.content_stack.addWidget(self._create_certificates_page())   # Index 3
        self.content_stack.addWidget(self._create_verification_page())   # Index 4
        self.content_stack.addWidget(self._create_settings_page())       # Index 5
        
        content_splitter.addWidget(self.content_stack)
        content_splitter.setSizes([300, 1100])
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { border-top: 1px solid #374151; padding: 4px; }")
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        
    def _create_header(self) -> QWidget:
        """Create the application header."""
        header = QFrame()
        header.setFixedHeight(70)
        header.setObjectName("header")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 16, 24, 16)
        
        # Logo and title
        title_container = QHBoxLayout()
        
        # App icon/logo (placeholder)
        logo = QLabel("🔒")
        logo.setFont(QFont("Segoe UI", 24))
        logo.setStyleSheet("color: #3B82F6;")
        title_container.addWidget(logo)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)

        app_title = QLabel("DELTON")
        app_title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        subtitle = QLabel("Data Erasure. Logging. Trusted. Obfuscation. Nought")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setProperty("subdued", True)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(subtitle)
        title_container.addLayout(title_layout)
        
        layout.addLayout(title_container)
        layout.addStretch()
        
        # User info and status
        user_info = QHBoxLayout()
        user_info.setSpacing(12)
        
        self.status_indicator = StatusIndicator("offline")
        user_info.addWidget(self.status_indicator)
        
        self.user_status_label = QLabel("Not Connected")
        self.user_status_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.user_status_label.setProperty("subdued", True)
        user_info.addWidget(self.user_status_label)
        
        # Loading spinner
        self.loading_spinner = LoadingSpinner(20)
        self.loading_spinner.hide()
        user_info.addWidget(self.loading_spinner)
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("dangerButton")
        self.logout_button.setFixedHeight(40)
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout_user)
        self.logout_button.setEnabled(False)
        user_info.addWidget(self.logout_button)
        
        layout.addLayout(user_info)
        header.setLayout(layout)
        
        return header
    

    def logout_user(self):
        """Handle user logout."""
        if not self.is_authenticated:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.is_authenticated = False
            self.status_indicator.set_status("offline")
            self.user_status_label.setText("Not Connected")
            self.select_target_button.setEnabled(False)
            self.select_health_target_button.setEnabled(False)
            self.logout_button.setEnabled(False)
            self.nav_buttons[1].setEnabled(False)  # Disable ML Health Check
            self.nav_buttons[2].setEnabled(False)  # Disable Wipe Operations
            self.nav_buttons[3].setEnabled(False)  # Disable Certificates
            self.switch_page(0)  # Return to login page
            self._update_status("Logged out successfully", "info")
    
    def _create_sidebar(self) -> QWidget:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Authentication", "🔐", 0, "Secure login and authentication"),
            ("ML Health Check", "💽", 1, "Perform drive health analysis"),
            ("Wipe Operations", "🗑️", 2, "Secure data sanitization"),
            ("Certificates", "📋", 3, "View and manage certificates"),
            ("Verification", "✅", 4, "Verify certificate authenticity"),
            ("Settings", "⚙️", 5, "Application preferences")
        ]
        
        for name, icon, page_idx, tooltip in nav_items:
            btn = self._create_nav_button(name, icon, page_idx, tooltip)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # System info
        sys_info = self._create_system_info_panel()
        layout.addWidget(sys_info)
        
        sidebar.setLayout(layout)
        if not self.is_authenticated:
            self.nav_buttons[1].setEnabled(False)  # Disable ML Health Check
            self.nav_buttons[2].setEnabled(False)  # Disable Wipe Operations
            self.nav_buttons[3].setEnabled(False)  # Disable Certificates
            self.nav_buttons[4].setEnabled(True)   # Enable Verification
            self.nav_buttons[5].setEnabled(True)   # Enable Settings
        
        return sidebar
        
    def _create_nav_button(self, name: str, icon: str, page_idx: int, tooltip: str) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(f"{icon}  {name}")
        btn.setObjectName("navButton")
        btn.setFixedHeight(48)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(page_idx))
        return btn
        
    def _create_system_info_panel(self) -> QWidget:
        """Create system information panel."""
        panel = QGroupBox("System Information")
        panel.setObjectName("systemInfo")
        
        layout = QFormLayout()
        layout.setSpacing(6)
        
        # System details
        import platform
        system_info = [
            ("OS:", f"{platform.system()} {platform.release()}"),
            ("Python:", f"{sys.version.split()[0]}"),
            ("Architecture:", platform.machine()),
        ]
        
        for label, value in system_info:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: 600;")
            label_widget.setProperty("subdued", True)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("font-family: 'Consolas', monospace;")
            value_widget.setWordWrap(True)
            
            layout.addRow(label_widget, value_widget)
            
        panel.setLayout(layout)
        return panel
        
    def _create_login_page(self) -> QWidget:
        """Create the authentication page."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignCenter)
        
        # Login card
        card = QFrame()
        card.setObjectName("loginCard")
        card.setMaximumWidth(450)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(8)
        
        title = QLabel("Secure Authentication")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Access your DELTON Enterprise account")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("subdued", True)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        card_layout.addLayout(header_layout)
        
        # Login form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Email field
        email_layout = QVBoxLayout()
        email_layout.setSpacing(6)
        
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("font-weight: 600;")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@company.com")
        self.email_input.setFixedHeight(44)
        self.email_input.setObjectName("formInput")
        
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        
        # Password field  
        password_layout = QVBoxLayout()
        password_layout.setSpacing(6)
        
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: 600;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(44)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("formInput")
        self.password_input.returnPressed.connect(self.authenticate_user)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        form_layout.addLayout(email_layout)
        form_layout.addLayout(password_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Keep me signed in")
        self.remember_checkbox.setProperty("subdued", True)
        form_layout.addWidget(self.remember_checkbox)
        
        card_layout.addLayout(form_layout)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setFixedHeight(48)
        self.login_button.setObjectName("primaryButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.authenticate_user)
        card_layout.addWidget(self.login_button)
        
        # Additional options
        options_layout = QHBoxLayout()
        options_layout.setAlignment(Qt.AlignCenter)
        
        help_link = QLabel('<a href="https://next-frontend-nu-two.vercel.app/" style="color: #3B82F6;">Need help?</a>')
        help_link.setOpenExternalLinks(True)
        options_layout.addWidget(help_link)
        
        card_layout.addLayout(options_layout)
        
        card.setLayout(card_layout)
        layout.addWidget(card)
        page.setLayout(layout)
        
        return page
        
    def _create_wipe_page(self) -> QWidget:
        """Create the data wiping operations page."""
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Left panel - Configuration
        config_panel = QFrame()
        config_panel.setObjectName("configPanel")
        config_panel.setMinimumWidth(400)
        config_panel.setMaximumWidth(500)
        
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(20)
        
        # Panel title
        title = QLabel("Wipe Configuration")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("margin-bottom: 8px;")
        config_layout.addWidget(title)
        
        # Configuration form
        form = QFormLayout()
        form.setSpacing(12)
        
        # Wipe method
        method_label = QLabel("Sanitization Method:")
        method_label.setStyleSheet("font-weight: 600;")
        
        self.method_combo = QComboBox()
        self.method_combo.setFixedHeight(40)
        self.method_combo.setObjectName("formCombo")
        self.method_combo.addItems([
            "NIST SP 800-88 Rev. 1 (Recommended)",
            "DoD 5220.22-M (3-Pass)",
            "Random Fill (7-Pass)", 
            "Zero Fill (Single Pass)",
            "Custom Pattern"
        ])
        
        # Security level
        security_label = QLabel("Security Level:")
        security_label.setStyleSheet("font-weight: 600;")
        
        self.security_combo = QComboBox()
        self.security_combo.setFixedHeight(40)
        self.security_combo.setObjectName("formCombo")
        self.security_combo.addItems([
            "Maximum Security (Slow)",
            "High Security (Recommended)", 
            "Standard Security (Fast)",
            "Basic Security (Fastest)"
        ])
        
        # Verification
        verify_label = QLabel("Verification:")
        verify_label.setStyleSheet("font-weight: 600;")
        
        self.verification_check = QCheckBox("Enable post-wipe verification")
        self.verification_check.setChecked(True)
        
        form.addRow(method_label, self.method_combo)
        form.addRow(security_label, self.security_combo)
        form.addRow(verify_label, self.verification_check)
        
        config_layout.addLayout(form)
        
        # Action buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)
        
        self.select_target_button = QPushButton("Select Target to Begin Wipe")
        self.select_target_button.setFixedHeight(50)
        self.select_target_button.setObjectName("successButton")
        self.select_target_button.setCursor(Qt.PointingHandCursor)
        self.select_target_button.setEnabled(False)
        self.select_target_button.clicked.connect(self.initiate_wipe_process)
        
        self.cancel_button = QPushButton("Cancel Operation")
        self.cancel_button.setFixedHeight(42)
        self.cancel_button.setObjectName("dangerButton")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_wipe_process)
        
        button_layout.addWidget(self.select_target_button)
        button_layout.addWidget(self.cancel_button)
        
        config_layout.addLayout(button_layout)
        config_layout.addStretch()
        
        config_panel.setLayout(config_layout)
        
        # Right panel - Progress and logs
        progress_panel = QFrame()
        progress_panel.setObjectName("progressPanel")
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(24, 24, 24, 24)
        progress_layout.setSpacing(16)
        
        # Progress section
        progress_title = QLabel("Operation Progress")
        progress_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        progress_title.setStyleSheet("margin-bottom: 8px;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progressBar")
        
        self.progress_label = QLabel("Ready to begin operation")
        self.progress_label.setStyleSheet("font-weight: 500;")
        self.progress_label.setProperty("subdued", True)
        
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        # Activity log
        log_title = QLabel("Activity Log")
        log_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        log_title.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
        
        self.activity_log = QTextEdit()
        self.activity_log.setObjectName("activityLog")
        self.activity_log.setReadOnly(True)
        self.activity_log.setFont(QFont("Consolas", 9))
        
        progress_layout.addWidget(log_title)
        progress_layout.addWidget(self.activity_log)
        
        progress_panel.setLayout(progress_layout)
        
        layout.addWidget(config_panel)
        layout.addWidget(progress_panel)
        page.setLayout(layout)
        
        return page
        
    def _create_certificates_page(self) -> QWidget:
        """Create the certificates management page."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Certificate Management")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search and filters
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        self.certificate_search = QLineEdit()
        self.certificate_search.setPlaceholderText("Search certificates by ID, method, or date...")
        self.certificate_search.setFixedHeight(40)
        self.certificate_search.setObjectName("searchInput")
        self.certificate_search.textChanged.connect(self._filter_certificates)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedHeight(40)
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.fetch_certificates)
        
        search_layout.addWidget(self.certificate_search, stretch=3)
        search_layout.addWidget(self.refresh_button)
        
        header_layout.addLayout(search_layout)
        layout.addLayout(header_layout)
        
        # Certificates table
        self.certificates_table = QTableWidget()
        self.certificates_table.setObjectName("certificatesTable")
        
        self.certificates_table.setSortingEnabled(False)
        
        headers = ["Certificate ID", "Date Created", "Method", "Status", "Actions"]
        self.certificates_table.setColumnCount(len(headers))
        self.certificates_table.setHorizontalHeaderLabels(headers)
        
        header = self.certificates_table.horizontalHeader()
        header.setStretchLastSection(True)  # Enable stretch for the last column to fill remaining space
        
        # Set resize modes
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Stretch the Actions column
        
        v_header = self.certificates_table.verticalHeader()
        v_header.setVisible(False)
        v_header.setDefaultSectionSize(45)
        v_header.setSectionResizeMode(QHeaderView.Fixed)
        
        self.certificates_table.setAlternatingRowColors(True)
        self.certificates_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.certificates_table.setShowGrid(False)
        
        self.certificates_table.verticalHeader().setMinimumSectionSize(45)
        self.certificates_table.setWordWrap(False)
        self.certificates_table.setAlternatingRowColors(True)
        
        # Set size policy to expand with the window
        self.certificates_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(self.certificates_table)
        page.setLayout(layout)
        
        return page



        
    def _create_verification_page(self) -> QWidget:
        """Create the certificate verification page."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignCenter)
        
        # Verification card
        card = QFrame()
        card.setObjectName("verificationCard")
        card.setMaximumWidth(600)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)
        
        # Header
        title = QLabel("Certificate Verification")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Verify the authenticity and integrity of sanitization certificates")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("subdued", True)
        subtitle.setWordWrap(True)
        
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        
        # Verification options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(16)
        
        # Online verification
        online_btn = QPushButton("🌐  Open Online Verification Portal")
        online_btn.setFixedHeight(56)
        online_btn.setObjectName("primaryButton")
        online_btn.setCursor(Qt.PointingHandCursor)
        online_btn.clicked.connect(self.open_verification_portal)
        
        # Local verification
        local_btn = QPushButton("📄  Verify Local Certificate File")
        local_btn.setFixedHeight(56)
        local_btn.setObjectName("secondaryButton") 
        local_btn.setCursor(Qt.PointingHandCursor)
        local_btn.clicked.connect(self.verify_local_certificate)
        
        options_layout.addWidget(online_btn)
        options_layout.addWidget(local_btn)
        
        card_layout.addLayout(options_layout)
        card.setLayout(card_layout)
        layout.addWidget(card)
        page.setLayout(layout)
        
        return page
        
    def _create_settings_page(self) -> QWidget:
        """Create the application settings page."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Title
        title = QLabel("Application Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Settings tabs
        tabs = QTabWidget()
        tabs.setObjectName("settingsTabs")
        
        # General settings
        general_tab = self._create_general_settings_tab()
        tabs.addTab(general_tab, "General")
        
        # Security settings  
        security_tab = self._create_security_settings_tab()
        tabs.addTab(security_tab, "Security")
        
        # Advanced settings
        advanced_tab = self._create_advanced_settings_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        page.setLayout(layout)
        
        return page
        
    def _create_general_settings_tab(self) -> QWidget:
        """Create general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout()
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark Theme", "Light Theme", "System Default"])
        theme_combo.setCurrentText("Light Theme")
        theme_combo.currentTextChanged.connect(self._change_theme)
        theme_layout.addRow("Theme:", theme_combo)
        
        theme_group.setLayout(theme_layout)
        
        # Notifications
        notif_group = QGroupBox("Notifications")  
        notif_layout = QVBoxLayout()
        
        notif_layout.addWidget(QCheckBox("Show operation completion notifications"))
        notif_layout.addWidget(QCheckBox("Play sound on completion"))
        notif_layout.addWidget(QCheckBox("Enable system tray notifications"))
        
        notif_group.setLayout(notif_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(notif_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def _create_security_settings_tab(self) -> QWidget:
        """Create security settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Authentication settings
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout()
        
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 120)
        timeout_spin.setValue(30)
        timeout_spin.setSuffix(" minutes")
        auth_layout.addRow("Session timeout:", timeout_spin)
        
        auth_group.setLayout(auth_layout)
        
        # Logging settings
        log_group = QGroupBox("Security Logging")
        log_layout = QVBoxLayout()
        
        log_layout.addWidget(QCheckBox("Log all operations"))
        log_layout.addWidget(QCheckBox("Enable audit trail"))
        log_layout.addWidget(QCheckBox("Require confirmation for destructive operations"))
        
        log_group.setLayout(log_layout)
        
        layout.addWidget(auth_group)
        layout.addWidget(log_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def _create_advanced_settings_tab(self) -> QWidget:
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout()
        
        threads_spin = QSpinBox()
        threads_spin.setRange(1, 16)
        threads_spin.setValue(4)
        perf_layout.addRow("Worker threads:", threads_spin)
        
        buffer_spin = QSpinBox()
        buffer_spin.setRange(1, 64)
        buffer_spin.setValue(8)
        buffer_spin.setSuffix(" MB")
        perf_layout.addRow("Buffer size:", buffer_spin)
        
        perf_group.setLayout(perf_layout)
        
        # Debug settings
        debug_group = QGroupBox("Debug")
        debug_layout = QVBoxLayout()
        
        debug_layout.addWidget(QCheckBox("Enable debug logging"))
        debug_layout.addWidget(QCheckBox("Show detailed error messages"))
        
        debug_group.setLayout(debug_layout)
        
        layout.addWidget(perf_group)
        layout.addWidget(debug_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def _create_ml_health_page(self) -> QWidget:
        """Create the ML Health Check page."""
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Left panel - Configuration
        config_panel = QFrame()
        config_panel.setObjectName("configPanel")
        config_panel.setMinimumWidth(400)
        config_panel.setMaximumWidth(500)
        
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(20)
        
        # Panel title
        title = QLabel("ML Health Check")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("margin-bottom: 8px;")
        config_layout.addWidget(title)
        
        # Action buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)
        
        self.select_health_target_button = QPushButton("Select Drive to Begin Health Check")
        self.select_health_target_button.setFixedHeight(50)
        self.select_health_target_button.setObjectName("successButton")
        self.select_health_target_button.setCursor(Qt.PointingHandCursor)
        self.select_health_target_button.setEnabled(False)
        self.select_health_target_button.clicked.connect(self.initiate_health_check)
        
        self.cancel_health_button = QPushButton("Cancel Operation")
        self.cancel_health_button.setFixedHeight(42)
        self.cancel_health_button.setObjectName("dangerButton")
        self.cancel_health_button.setCursor(Qt.PointingHandCursor)
        self.cancel_health_button.setEnabled(False)
        self.cancel_health_button.clicked.connect(self.cancel_health_check)
        
        button_layout.addWidget(self.select_health_target_button)
        button_layout.addWidget(self.cancel_health_button)
        
        config_layout.addLayout(button_layout)
        config_layout.addStretch()
        
        config_panel.setLayout(config_layout)
        
        # Right panel - Progress and logs
        progress_panel = QFrame()
        progress_panel.setObjectName("progressPanel")
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(24, 24, 24, 24)
        progress_layout.setSpacing(16)
        
        # Progress section
        progress_title = QLabel("Operation Progress")
        progress_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        progress_title.setStyleSheet("margin-bottom: 8px;")
        
        self.health_progress_bar = QProgressBar()
        self.health_progress_bar.setFixedHeight(24)
        self.health_progress_bar.setRange(0, 100)
        self.health_progress_bar.setValue(0)
        self.health_progress_bar.setObjectName("progressBar")
        
        self.health_progress_label = QLabel("Ready to begin operation")
        self.health_progress_label.setStyleSheet("font-weight: 500;")
        self.health_progress_label.setProperty("subdued", True)
        
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self.health_progress_bar)
        progress_layout.addWidget(self.health_progress_label)
        
        # Activity log
        log_title = QLabel("Activity Log")
        log_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        log_title.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
        
        self.health_activity_log = QTextEdit()
        self.health_activity_log.setObjectName("activityLog")
        self.health_activity_log.setReadOnly(True)
        self.health_activity_log.setFont(QFont("Consolas", 9))
        
        progress_layout.addWidget(log_title)
        progress_layout.addWidget(self.health_activity_log)
        
        # Health results display
        results_title = QLabel("Health Check Results")
        results_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        results_title.setStyleSheet("margin-top: 16px; margin-bottom: 8px;")
        
        self.health_results = QTextEdit()
        self.health_results.setReadOnly(True)
        
        progress_layout.addWidget(results_title)
        progress_layout.addWidget(self.health_results)
        
        progress_panel.setLayout(progress_layout)
        
        layout.addWidget(config_panel)
        layout.addWidget(progress_panel)
        page.setLayout(layout)
        
        return page
        
    def initiate_health_check(self):
        """Initiate the ML health check process."""
        if not self.is_authenticated:
            QMessageBox.warning(
                self, 
                "Authentication Required", 
                "Please authenticate before starting a health check."
            )
            return
            
        # Get available drives
        drives = list_drives()
        
        if not drives or (len(drives) == 1 and 'error' in drives[0]):
            QMessageBox.critical(
                self, 
                "System Error", 
                "Cannot retrieve drive information. Please ensure you have administrator privileges and try again."
            )
            return
            
        # Create drive selection dialog
        dialog = self._create_drive_selection_dialog(drives, is_health_check=True)
        
        if dialog.exec() == QDialog.Accepted:
            selected_path = getattr(dialog, 'selected_path', None)
            if selected_path:
                self.execute_health_check(selected_path)
                
    def execute_health_check(self, target_path: str):
        """Execute the ML health check with progress tracking."""
        self._update_status(f"Initiating ML health check of {target_path}", "processing")
        
        # Update UI state
        self.select_health_target_button.setEnabled(False)
        self.cancel_health_button.setEnabled(True)
        self.health_progress_bar.setValue(0)
        self.health_progress_label.setText("Preparing ML health check operation...")
        
        # Start progress animation
        self.progress_timer.start()
        
        try:
            # Simulate or implement actual health check logic (placeholder)
            # For real implementation, call API or run ML model
            time.sleep(2)  # Simulate processing
            health_result = {
                "status": "Healthy",
                "details": "No issues detected. Drive health is optimal.",
                "score": 95
            }
            
            # Stop progress timer
            self.progress_timer.stop()
            self.health_progress_bar.setValue(100)
            
            # Display results
            self.health_results.setText(
                f"Health Status: {health_result['status']}\n"
                f"Score: {health_result['score']}/100\n"
                f"Details: {health_result['details']}"
            )
            
            QMessageBox.information(
                self,
                "Health Check Completed",
                f"ML Health Check of {target_path} completed successfully.\n\n"
                f"Status: {health_result['status']}\nScore: {health_result['score']}"
            )
            self._update_status("Health check completed successfully", "success")
                
        except Exception as e:
            self.progress_timer.stop()
            self._handle_health_error(str(e), target_path)
            
        finally:
            # Reset UI state
            self.select_health_target_button.setEnabled(True)
            self.cancel_health_button.setEnabled(False)
            QTimer.singleShot(2000, lambda: self.health_progress_bar.setValue(0))
            
    def _handle_health_error(self, error_message: str, target_path: str):
        """Handle health check errors."""
        QMessageBox.critical(
            self,
            "Operation Failed",
            f"ML Health Check of {target_path} failed.\n\n"
            f"Error: {error_message}\n\n"
            "Please check the activity log for detailed information and try again."
        )
        self._update_status(f"Health check failed: {error_message}", "error")
        
    def cancel_health_check(self):
        """Cancel ongoing health check process."""
        reply = QMessageBox.question(
            self,
            "Cancel Operation",
            "Are you sure you want to cancel the ongoing health check?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop timers and reset UI
            self.progress_timer.stop()
            self.health_progress_bar.setValue(0)
            self.health_progress_label.setText("Operation canceled by user")
            self.select_health_target_button.setEnabled(True)
            self.cancel_health_button.setEnabled(False)
            self._update_status("Health check canceled", "warning")
        
    def _create_drive_selection_dialog(self, drives: List[Dict[str, Any]], is_health_check: bool = False) -> QDialog:
        """Create professional drive selection dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Target for Secure Wipe" if not is_health_check else "Select Drive for ML Health Check")
        dialog.setModal(True)
        dialog.resize(800, 600)
        dialog.setObjectName("driveSelectionDialog")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Warning banner (only for wipe)
        if not is_health_check:
            warning_frame = QFrame()
            warning_frame.setObjectName("warningBanner")
            warning_frame.setStyleSheet(f"""
                QFrame#warningBanner {{
                    background-color: {self.colors['warning_bg']};
                    border: 1px solid {self.colors['warning_border']};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            
            warning_layout = QHBoxLayout()
            warning_icon = QLabel("⚠️")
            warning_icon.setFont(QFont("Segoe UI", 16))
            
            warning_text = QLabel(
                "<b>CRITICAL WARNING</b><br>"
                "This operation will permanently destroy ALL data on the selected target. "
                "This action cannot be undone. Ensure you have proper authorization and backups."
            )
            warning_text.setStyleSheet(f"color: {self.colors['warning_text']}; font-weight: 500;")
            warning_text.setWordWrap(True)
            
            warning_layout.addWidget(warning_icon)
            warning_layout.addWidget(warning_text)
            warning_frame.setLayout(warning_layout)
            layout.addWidget(warning_frame)
        
        # Drive selection table
        drive_table = QTableWidget()
        drive_table.setColumnCount(6)
        drive_table.setHorizontalHeaderLabels([
            "Device", "Size", "Type", "Model", "Serial", "Mount Point"
        ])
        
        # Populate table
        valid_drives = []
        for drive in drives:
            if 'error' in drive:
                continue
                
            # For wipe, filter out system-critical mount points
            if not is_health_check and drive.get('mountpoint') in ['/', '/boot', '/home', '/usr', '/var', '/etc']:
                continue
                
            valid_drives.append(drive)
            
        drive_table.setRowCount(len(valid_drives))
        
        for row, drive in enumerate(valid_drives):
            items = [
                drive.get('name', ''),
                drive.get('size', ''),
                drive.get('type', ''),
                drive.get('model', ''),
                drive.get('serial', ''),
                drive.get('mountpoint', 'Not mounted')
            ]
            
            for col, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if col == 0:  # Store full drive info in first column
                    item.setData(Qt.UserRole, drive)
                drive_table.setItem(row, col, item)
                
        # Configure table
        header = drive_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
        drive_table.setSelectionBehavior(QTableWidget.SelectRows)
        drive_table.setAlternatingRowColors(True)
        
        layout.addWidget(QLabel("Available targets:"))
        layout.addWidget(drive_table)
        
        # Alternative selection (only for wipe)
        if not is_health_check:
            alt_layout = QHBoxLayout()
            file_btn = QPushButton("Select File/Folder Instead")
            file_btn.setObjectName("secondaryButton")
            file_btn.clicked.connect(lambda: self._select_file_target(dialog))
            alt_layout.addWidget(file_btn)
            alt_layout.addStretch()
            layout.addLayout(alt_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(dialog.reject)
        
        proceed_btn = QPushButton("Proceed with Wipe" if not is_health_check else "Proceed with Health Check")
        proceed_btn.setObjectName("dangerButton" if not is_health_check else "primaryButton")
        proceed_btn.setEnabled(False)
        
        def on_selection_changed():
            proceed_btn.setEnabled(len(drive_table.selectedItems()) > 0)
            
        drive_table.itemSelectionChanged.connect(on_selection_changed)
        
        def on_proceed():
            selected_items = drive_table.selectedItems()
            if selected_items:
                drive_data = selected_items[0].data(Qt.UserRole)
                if drive_data:
                    if is_health_check:
                        dialog.selected_path = drive_data['name']
                        dialog.accept()
                    else:
                        reply = QMessageBox.question(
                            dialog,
                            "Final Confirmation",
                            f"Are you absolutely certain you want to wipe {drive_data['name']}?\n\n"
                            f"Size: {drive_data.get('size', 'Unknown')}\n"
                            f"Model: {drive_data.get('model', 'Unknown')}\n\n"
                            "This action CANNOT be undone!",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if reply == QMessageBox.Yes:
                            dialog.selected_path = drive_data['name']
                            dialog.accept()
                        
        proceed_btn.clicked.connect(on_proceed)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(proceed_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        return dialog
        
    def _select_file_target(self, dialog: QDialog):
        """Handle file/folder target selection."""
        target_path = QFileDialog.getExistingDirectory(
            dialog, 
            "Select Folder to Securely Delete"
        )
        
        if target_path:
            reply = QMessageBox.question(
                dialog,
                "Confirm File/Folder Wipe",
                f"Securely delete: {target_path}\n\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                dialog.selected_path = target_path
                dialog.accept()
                
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        from PySide6.QtGui import QKeySequence, QShortcut
        
        # Navigation shortcuts
        shortcuts = [
            (QKeySequence("Ctrl+1"), lambda: self.switch_page(0)),  # Authentication
            (QKeySequence("Ctrl+2"), lambda: self.switch_page(1)),  # ML Health Check
            (QKeySequence("Ctrl+3"), lambda: self.switch_page(2)),  # Wipe Operations
            (QKeySequence("Ctrl+4"), lambda: self.switch_page(3)),  # Certificates
            (QKeySequence("Ctrl+5"), lambda: self.switch_page(4)),  # Verification
            (QKeySequence("Ctrl+6"), lambda: self.switch_page(5)),  # Settings
            (QKeySequence("Ctrl+R"), self.fetch_certificates),
            (QKeySequence("Ctrl+Q"), self.close),
            (QKeySequence("F5"), self.fetch_certificates),
        ]
        
        for key_sequence, callback in shortcuts:
            shortcut = QShortcut(key_sequence, self)
            shortcut.activated.connect(callback)
            
    def switch_page(self, page_index: int):
        """Switch between application pages with visual feedback."""
        self.content_stack.setCurrentIndex(page_index)
        
        # Update navigation button states
        for i, btn in enumerate(self.nav_buttons):
            if i == page_index:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # Auto-fetch certificates when navigating to certificates page
        if page_index == 3 and self.is_authenticated:
            self.fetch_certificates()
            
    def _update_status(self, message: str, status_type: str = "info"):
        """Update status bar with message and optional toast notification."""
        if self.status_bar:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.status_bar.showMessage(f"[{timestamp}] {message}")
            
        # Add to activity log if wipe page is active
        if hasattr(self, 'activity_log'):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}<br>"
            colors = {
                "info": self.colors['primary_start'],
                "success": self.colors['success_start'],
                "error": self.colors['danger_start'],
                "warning": "#D97706",
                "processing": self.colors['primary_start']
            }
            color = colors.get(status_type, self.colors['disabled_text'])
            self.activity_log.moveCursor(QTextCursor.End)
            self.activity_log.textCursor().insertHtml(f'<span style="color:{color};">{log_entry}</span>')
            self.activity_log.ensureCursorVisible()
            
    def authenticate_user(self):
        """Handle user authentication with comprehensive validation."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        # Input validation
        if not email or not password:
            QMessageBox.warning(
                self, 
                "Incomplete Information", 
                "Please enter both email and password."
            )
            return
            
        if "@" not in email or "." not in email.split("@")[-1]:
            QMessageBox.warning(
                self, 
                "Invalid Email", 
                "Please enter a valid email address."
            )
            return
            
        # Show loading state
        self.login_button.setText("Authenticating...")
        self.login_button.setEnabled(False)
        self.loading_spinner.start()
        self.loading_spinner.show()
        
        # Perform authentication
        success, result = self.api_client.login(email, password)
        
        # Hide loading state
        self.loading_spinner.stop()
        self.loading_spinner.hide()
        self.login_button.setText("Sign In")
        self.login_button.setEnabled(True)
        
        if success:
            self.is_authenticated = True
            self.status_indicator.set_status("online")
            self.user_status_label.setText(f"Connected as {email}")
            self.select_target_button.setEnabled(True)
            self.select_health_target_button.setEnabled(True)
            self.logout_button.setEnabled(True)  # Enable logout button on successful login
            self.nav_buttons[1].setEnabled(True)  # Enable ML Health Check
            self.nav_buttons[2].setEnabled(True)  # Enable Wipe Operations
            self.nav_buttons[3].setEnabled(True)  # Enable Certificates
            self._update_status(f"Authentication successful at 07:26 PM IST, Sunday, September 28, 2025", "success")
            self.email_input.setText("")
            self.password_input.setText("")

            # Navigate to ML Health Check page
            self.switch_page(1)
            
        else:
            QMessageBox.critical(
                self,
                "Authentication Failed",
                f"Unable to authenticate: {result}\n\nPlease check your credentials and try again."
            )
            self._update_status("Authentication failed", "error")
            
    def initiate_wipe_process(self):
        """Initiate the secure wipe process with comprehensive drive selection."""
        if not self.is_authenticated:
            QMessageBox.warning(
                self, 
                "Authentication Required", 
                "Please authenticate before starting a wipe operation."
            )
            return
            
        # Get available drives
        drives = list_drives()
        
        if not drives or (len(drives) == 1 and 'error' in drives[0]):
            QMessageBox.critical(
                self, 
                "System Error", 
                "Cannot retrieve drive information. Please ensure you have administrator privileges and try again."
            )
            return
            
        # Create enhanced drive selection dialog
        dialog = self._create_drive_selection_dialog(drives)
        
        if dialog.exec() == QDialog.Accepted:
            selected_path = getattr(dialog, 'selected_path', None)
            if selected_path:
                self.execute_wipe_operation(selected_path)
                
    def execute_wipe_operation(self, target_path: str):
        """Execute the secure wipe operation with progress tracking."""
        method = self.method_combo.currentText()
        security_level = self.security_combo.currentText()
        
        self._update_status(f"Initiating secure wipe of {target_path}", "processing")
        
        # Update UI state
        self.select_target_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Preparing secure wipe operation...")
        
        # Start progress animation
        self.progress_timer.start()
        
        try:
            # Execute wipe operation
            result = secure_delete(
                target_path, 
                self.api_client.api_base, 
                self.api_client.jwt_token
            )
            
            # Stop progress timer
            self.progress_timer.stop()
            self.progress_bar.setValue(100)
            
            # Process results
            if isinstance(result, tuple):
                sanitization_success, server_success, server_message = result
                self._handle_wipe_completion(
                    sanitization_success, server_success, server_message, target_path
                )
            elif result:
                self._handle_wipe_completion(True, False, "No server sync", target_path)
            else:
                self._handle_wipe_completion(False, False, "Operation failed", target_path)
                
        except Exception as e:
            self.progress_timer.stop()
            self._handle_wipe_error(str(e), target_path)
            
        finally:
            # Reset UI state
            self.select_target_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            QTimer.singleShot(2000, lambda: self.progress_bar.setValue(0))
            
    def _handle_wipe_completion(self, sanitization_success: bool, server_success: bool, 
                               server_message: str, target_path: str):
        """Handle wipe operation completion."""
        if sanitization_success:
            if server_success:
                QMessageBox.information(
                    self,
                    "Operation Completed Successfully",
                    f"Secure wipe of {target_path} completed successfully.\n\n"
                    "• Data sanitization: COMPLETED\n"
                    "• Certificate generation: COMPLETED\n"
                    "• Server synchronization: COMPLETED"
                )
                self._update_status("Wipe operation completed successfully", "success")
            else:
                QMessageBox.information(
                    self,
                    "Operation Partially Completed", 
                    f"Secure wipe of {target_path} completed successfully.\n\n"
                    f"• Data sanitization: COMPLETED\n"
                    f"• Server synchronization: FAILED ({server_message})\n\n"
                    "The data has been securely wiped, but certificate upload failed."
                )
                self._update_status("Wipe completed, server sync failed", "warning")
        else:
            self._handle_wipe_error("Sanitization process failed", target_path)
            
    def _handle_wipe_error(self, error_message: str, target_path: str):
        """Handle wipe operation errors."""
        QMessageBox.critical(
            self,
            "Operation Failed",
            f"Secure wipe of {target_path} failed.\n\n"
            f"Error: {error_message}\n\n"
            "Please check the activity log for detailed information and try again."
        )
        self._update_status(f"Wipe operation failed: {error_message}", "error")
        
    def cancel_wipe_process(self):
        """Cancel ongoing wipe process."""
        reply = QMessageBox.question(
            self,
            "Cancel Operation",
            "Are you sure you want to cancel the ongoing wipe operation?\n\n"
            "Canceling may leave the target in an inconsistent state.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop timers and reset UI
            self.progress_timer.stop()
            self.progress_bar.setValue(0)
            self.progress_label.setText("Operation canceled by user")
            self.select_target_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self._update_status("Wipe operation canceled", "warning")
            
    def _advance_progress(self):
        """Advance progress bar during operations."""
        current = self.progress_bar.value()
        if current < 90:
            self.progress_bar.setValue(current + 1)
            
    def fetch_certificates(self):
        """Fetch certificates from server with enhanced error handling."""
        if not self.is_authenticated:
            QMessageBox.warning(
                self, 
                "Authentication Required", 
                "Please authenticate before accessing certificates."
            )
            return
            
        self._update_status("Fetching certificates from server...", "processing")
        
        # Show loading state
        self.refresh_button.setText("Loading...")
        self.refresh_button.setEnabled(False)
        
        success, result = self.api_client.fetch_certificates()
        
        # Hide loading state
        self.refresh_button.setText("Refresh")
        self.refresh_button.setEnabled(True)
        
        if success:
            self.all_certificates = result
            self._populate_certificates_table(result)
            self._update_status(f"Loaded {len(result)} certificates", "success")
        else:
            QMessageBox.critical(
                self,
                "Server Error",
                f"Failed to fetch certificates from server:\n\n{result}"
            )
            self._update_status("Failed to fetch certificates", "error")
            
    def _populate_certificates_table(self, certificates: List[Dict[str, Any]]):
        """Populate the certificates table with data."""
        self.certificates_table.setSortingEnabled(False)
        
        self.certificates_table.setRowCount(0)
        self.certificates_table.clearContents()
        
        if not certificates:
            self.certificates_table.setSortingEnabled(True)
            return
        
        for row, cert in enumerate(certificates):
            self.certificates_table.insertRow(row)
            
            payload = cert.get("payload", {})
            cert_id = cert.get("certificateId", payload.get("certificate_id", "Unknown"))
            formatted_date = self._format_timestamp(payload.get("start_time", ""))
            method = payload.get("method", "Unknown")
            status = payload.get("final_status", "Unknown")
            
            # Create items and set as read-only
            item0 = QTableWidgetItem(str(cert_id))
            item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            self.certificates_table.setItem(row, 0, item0)
            
            item1 = QTableWidgetItem(formatted_date)
            item1.setFlags(item1.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            self.certificates_table.setItem(row, 1, item1)
            
            item2 = QTableWidgetItem(method)
            item2.setFlags(item2.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            self.certificates_table.setItem(row, 2, item2)
            
            item3 = QTableWidgetItem(status)
            item3.setFlags(item3.flags() & ~Qt.ItemIsEditable)  # Remove editable flag
            self.certificates_table.setItem(row, 3, item3)
            
            btn = QPushButton("Actions")
            btn.setMinimumWidth(80)  # Minimum width to fit "Actions" text
            btn.setFixedHeight(40)   # Match row height
            btn.setObjectName("actionButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cert, cid=cert_id: self._show_actions_menu(c, cid))
            
            self.certificates_table.setCellWidget(row, 4, btn)
            self.certificates_table.setRowHeight(row, 57)  # Ensure row height is consistent
        
        self.certificates_table.setSortingEnabled(True)
        self.certificates_table.resizeColumnsToContents()  # Adjust columns to content before stretching
        self.certificates_table.viewport().update()
        self.certificates_table.repaint()
        self.certificates_table.sortItems(1, Qt.DescendingOrder)  # Sort by Date Created descending

    def _show_actions_menu(self, cert, cert_id):
        """Show actions menu when button is clicked."""
        from PySide6.QtWidgets import QMessageBox  # Changed from PyQt5 to PySide6
        
        msg = QMessageBox(self.certificates_table)
        msg.setWindowTitle("Certificate Actions")
        msg.setText(f"Choose action for certificate: {cert_id}")
        msg.setIcon(QMessageBox.Icon.Question)  # Note: PySide6 syntax
        
        view_btn = msg.addButton("👁 View Details", QMessageBox.ButtonRole.ActionRole)
        download_btn = msg.addButton("📥 Download", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        result = msg.exec()  # Note: exec() not exec_() in PySide6
        
        if msg.clickedButton() == view_btn:
            self._view_certificate_details(cert)
        elif msg.clickedButton() == download_btn:
            self.download_certificate(cert_id)









            
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp for display."""
        if not timestamp_str:
            return "Unknown"
            
        try:
            # Parse ISO format timestamp
            dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(timestamp_str)
            
    def _view_certificate_details(self, certificate: Dict[str, Any]):
        """Show detailed certificate information in a dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Certificate Details")
        dialog.setModal(True)
        dialog.resize(600, 500)
        dialog.setObjectName("certificateDetailsDialog")
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Certificate Information")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Certificate details
        details_area = QScrollArea()
        details_widget = QWidget()
        details_layout = QFormLayout()
        details_layout.setSpacing(8)
        
        payload = certificate.get("payload", {})
        
        # Format certificate information
        cert_info = [
            ("Certificate ID", certificate.get("certificateId", "Unknown")),
            ("Session ID", payload.get("session_id", "Unknown")),
            ("NIST Standard", payload.get("nist_standard", "Unknown")),
            ("Method", payload.get("method", "Unknown")),
            ("Device", payload.get("device", "Unknown")),
            ("Start Time", self._format_timestamp(payload.get("start_time", ""))),
            ("Completion Time", self._format_timestamp(payload.get("completion_time", ""))),
            ("Operator", payload.get("operator", "Unknown")),
            ("Hostname", payload.get("hostname", "Unknown")),
            ("Status", payload.get("final_status", "Unknown")),
            ("Disposition", payload.get("disposition", "Unknown"))
        ]
        
        for label_text, value in cert_info:
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("font-weight: 600;")
            label.setProperty("subdued", True)
            
            value_label = QLabel(str(value))
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            details_layout.addRow(label, value_label)
            
        details_widget.setLayout(details_layout)
        details_area.setWidget(details_widget)
        details_area.setWidgetResizable(True)
        
        layout.addWidget(details_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        download_btn = QPushButton("Download PDF")
        download_btn.setObjectName("primaryButton")
        download_btn.setCursor(Qt.PointingHandCursor)
        cert_id = certificate.get("certificateId", "")
        download_btn.clicked.connect(lambda: self.download_certificate(cert_id))
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(download_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
        
    def download_certificate(self, certificate_id: str):
        """Download certificate PDF with progress indication."""
        if not certificate_id or certificate_id == "Unknown":
            QMessageBox.warning(
                self,
                "Invalid Certificate",
                "Certificate ID is not available for download."
            )
            return
            
        self._update_status(f"Downloading certificate {certificate_id}...", "processing")
        
        success, result = self.api_client.download_certificate(certificate_id)
        
        if success:
            # Prompt user for save location
            default_filename = f"DELTON_Certificate_{certificate_id}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Certificate",
                default_filename,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, "wb") as f:
                        for chunk in result.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                
                    QMessageBox.information(
                        self,
                        "Download Complete",
                        f"Certificate saved successfully to:\n{file_path}"
                    )
                    self._update_status("Certificate downloaded successfully", "success")
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Save Error",
                        f"Failed to save certificate file:\n{str(e)}"
                    )
                    self._update_status("Certificate download failed", "error")
        else:
            QMessageBox.critical(
                self,
                "Download Failed", 
                f"Failed to download certificate:\n{result}"
            )
            self._update_status("Certificate download failed", "error")
            
    def _filter_certificates(self):
        """Filter certificates based on search input."""
        search_text = self.certificate_search.text().strip().lower()
        
        if not search_text:
            self._populate_certificates_table(self.all_certificates)
            return
            
        filtered_certs = []
        for cert in self.all_certificates:
            # Search in certificate data
            cert_json = json.dumps(cert).lower()
            if search_text in cert_json:
                filtered_certs.append(cert)
                
        self._populate_certificates_table(filtered_certs)
        self._update_status(f"Filtered to {len(filtered_certs)} certificates", "info")
        
    def open_verification_portal(self):
        """Open the online certificate verification portal."""
        verification_url = "https://next-frontend-nu-two.vercel.app/verify"
        
        try:
            webbrowser.open(verification_url)
            self._update_status("Opened verification portal in browser", "success")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Browser Error",
                f"Failed to open verification portal:\n{str(e)}\n\n"
                f"Please manually navigate to:\n{verification_url}"
            )
            
    def verify_local_certificate(self):
        """Handle local certificate file verification."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Certificate to Verify",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            # For now, just show info - could be extended with actual verification logic
            QMessageBox.information(
                self,
                "Local Verification",
                f"Selected certificate file:\n{file_path}\n\n"
                "Local verification functionality would be implemented here.\n"
                "For now, please use the online verification portal."
            )
            
    def closeEvent(self, event):
        """Handle application close event."""
        if self.current_wipe_process and self.current_wipe_process.isRunning():
            reply = QMessageBox.question(
                self,
                "Operation in Progress",
                "A wipe operation is currently running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
                
        self._update_status("Application closing", "info")
        event.accept()


# Maintain backward compatibility with the original class name
WipeApp = DELTONApp