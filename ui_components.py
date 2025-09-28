#!/usr/bin/env python3
import sys
import datetime
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QComboBox,
    QFrame, QSizePolicy, QProgressBar, QSpacerItem, QStackedWidget,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QTimer, Signal, QObject


class StatusDot(QLabel):
    """Small colored dot used for status indicators."""
    def __init__(self, color="#d0d0d0", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setStyleSheet(f"border-radius:6px; background:{color};")


class DriveSelectionDialog(QDialog):
    """Dialog for selecting drives to wipe"""
    def __init__(self, drives, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Drive to Wipe")
        self.setModal(True)
        self.resize(700, 500)
        self.selected_path = None
        
        self._setup_ui(drives)
        
    def _setup_ui(self, drives):
        layout = QVBoxLayout()

        # Warning message
        warning = QLabel("⚠️ WARNING: This will permanently destroy all data on the selected drive!")
        warning.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 10px; background: #2d1b1b; border-radius: 8px; border: 1px solid #ff6b6b;")
        layout.addWidget(warning)

        # Drive list
        self.drive_list = QListWidget()
        
        for drive in drives:
            if 'error' in drive:
                continue
                
            # Skip mounted system drives for safety
            if drive.get('mountpoint') in ['/', '/boot', '/home', '/usr', '/var']:
                continue
                
            item_text = f"{drive['name']} - {drive['size']} - {drive['model']} ({drive['type']})"
            if drive.get('mountpoint'):
                item_text += f" [MOUNTED: {drive['mountpoint']}]"
                
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, drive['name'])
            self.drive_list.addItem(item)

        layout.addWidget(QLabel("Available drives:"))
        layout.addWidget(self.drive_list)

        # Option to select file/folder instead
        file_folder_btn = QPushButton("Select File/Folder Instead")
        file_folder_btn.setObjectName("primaryBtn")
        file_folder_btn.setFixedHeight(36)
        file_folder_btn.clicked.connect(self._select_file_folder)
        layout.addWidget(file_folder_btn)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        wipe_btn = QPushButton("Wipe Selected")
        wipe_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: 700; border-radius: 8px;")
        wipe_btn.setFixedHeight(40)
        cancel_btn.setFixedHeight(40)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(wipe_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        cancel_btn.clicked.connect(self.reject)
        wipe_btn.clicked.connect(self._confirm_wipe)

    def _select_file_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Wipe")
        if path:
            self.selected_path = path
            self.accept()

    def _confirm_wipe(self):
        current_item = self.drive_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a drive to wipe.")
            return
            
        drive_path = current_item.data(Qt.UserRole)
        
        # Final confirmation
        reply = QMessageBox.question(
            self, 
            "Final Confirmation",
            f"Are you absolutely sure you want to wipe {drive_path}?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.selected_path = drive_path
            self.accept()


class LoginPage(QWidget):
    login_requested = Signal(str, str)  # email, password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)

        lbl = QLabel("Sign in to your account")
        lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        card_layout.addWidget(lbl)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Email")
        self.username.setFixedHeight(36)
        card_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setFixedHeight(36)
        self.password.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.password)

        self.login_btn = QPushButton("Sign in")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setFixedHeight(40)
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self.login_btn)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignTop)
        layout.addStretch()
        self.setLayout(layout)

    def _handle_login(self):
        email = self.username.text().strip()
        password = self.password.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Missing fields", "Please enter email and password.")
            return
            
        self.login_requested.emit(email, password)

    def clear_fields(self):
        self.username.clear()
        self.password.clear()


class WipePage(QWidget):
    wipe_requested = Signal(str)  # path to wipe
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_progress_timer()
    
    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(16)

        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        wipe_card = QFrame()
        wipe_card.setObjectName("card")
        wipe_card_layout = QVBoxLayout()
        wipe_card_layout.setContentsMargins(14, 14, 14, 14)
        wipe_card_layout.setSpacing(10)

        title = QLabel("Wipe configuration")
        title.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        wipe_card_layout.addWidget(title)

        cap_label = QLabel("Device capacity (GB, optional)")
        wipe_card_layout.addWidget(cap_label)
        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("e.g. 512")
        self.capacity_input.setFixedHeight(34)
        wipe_card_layout.addWidget(self.capacity_input)

        wipe_card_layout.addWidget(QLabel("Wipe method"))
        self.method_box = QComboBox()
        self.method_box.setFixedHeight(34)
        self.method_box.addItems(["zero-fill-1pass", "random-fill-3pass", "dod-5220.22-m"])
        wipe_card_layout.addWidget(self.method_box)

        wipe_card_layout.addWidget(QLabel("Wipe policy"))
        self.policy_box = QComboBox()
        self.policy_box.setFixedHeight(34)
        self.policy_box.addItems(["NIST SP 800-88", "DoD 5220.22-M", "Custom Policy"])
        wipe_card_layout.addWidget(self.policy_box)

        # actions row
        actions = QHBoxLayout()
        self.select_btn = QPushButton("Select drive & wipe")
        self.select_btn.setEnabled(False)
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.setObjectName("successBtn")
        self.select_btn.setFixedHeight(40)
        self.select_btn.clicked.connect(self._handle_select_and_wipe)
        actions.addWidget(self.select_btn)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(18)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        actions.addWidget(self.progress, stretch=1)

        wipe_card_layout.addLayout(actions)
        wipe_card.setLayout(wipe_card_layout)

        left_col.addWidget(wipe_card)
        left_col.addStretch()
        layout.addLayout(left_col, 2)

        # right info / branding
        right_col = QVBoxLayout()
        info = QLabel()
        info.setText(
            "<div style='font-size:14px;color:#e2e8f0;'>"
            "<b>SecureWipe</b><br>"
            "<span style='color:#94a3b8'>Fast, verifiable secure deletions</span><br><br>"
            "<span style='color:#cbd5e1;font-size:11px'>"
            "• Wipe methods: zero / random / DoD<br>"
            "• Server-signed certificates and PDFs<br>"
            "• Cloud upload for signed certificates"
            "</span></div>"
        )
        info.setAlignment(Qt.AlignTop)
        right_col.addWidget(info)
        right_col.addStretch()
        layout.addLayout(right_col, 1)

        self.setLayout(layout)
    
    def _setup_progress_timer(self):
        self._progress_timer = QTimer()
        self._progress_timer.setInterval(30)
        self._progress_timer.timeout.connect(self._advance_progress)

    def _handle_select_and_wipe(self):
        self.wipe_requested.emit("select_drive")

    def enable_wipe_button(self, enabled=True):
        self.select_btn.setEnabled(enabled)

    def start_progress(self):
        self.progress.setValue(5)
        self._progress_timer.start()

    def stop_progress(self):
        self._progress_timer.stop()
        self.progress.setValue(100)
        # Reset progress after a delay
        QTimer.singleShot(600, lambda: self.progress.setValue(0))

    def _advance_progress(self):
        v = self.progress.value()
        if v < 95:
            self.progress.setValue(v + 2)
        else:
            self.progress.setValue(95)

    def get_wipe_config(self):
        try:
            capacity_gb = int(self.capacity_input.text().strip()) if self.capacity_input.text().strip() else 0
        except ValueError:
            capacity_gb = 0
            
        return {
            'capacity': capacity_gb,
            'method': self.method_box.currentText(),
            'policy': self.policy_box.currentText()
        }


class CertificatesPage(QWidget):
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.all_certs = []
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_label = QLabel("Certificates")
        header_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        header_row.addWidget(header_label)
        header_row.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, status or method...")
        self.search_input.setFixedHeight(34)
        self.search_input.textChanged.connect(self._filter_certs)
        header_row.addWidget(self.search_input, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        # Scroll area for certificate list
        self.certs_area = QScrollArea()
        self.certs_area.setWidgetResizable(True)
        self.certs_container = QWidget()
        self.certs_layout = QVBoxLayout()
        self.certs_layout.setSpacing(12)
        self.certs_layout.addStretch()
        self.certs_container.setLayout(self.certs_layout)
        self.certs_area.setWidget(self.certs_container)
        layout.addWidget(self.certs_area)

        self.setLayout(layout)

    def update_certificates(self, certificates):
        self.all_certs = certificates
        self._render_certificates(certificates)

    def _render_certificates(self, certs):
        # clear old items
        for i in reversed(range(self.certs_layout.count())):
            item = self.certs_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not certs:
            lbl = QLabel("No certificates found.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 13px;")
            self.certs_layout.addWidget(lbl)
            self.certs_layout.addStretch()
            return

        for c in certs:
            card = QFrame()
            card.setObjectName("card")
            card.setStyleSheet("padding:10px;")
            gl = QGridLayout()
            gl.setSpacing(6)

            # fields: certificateId, status, createdAt, completedAt, wipeMethod, pdfUrl
            cert_id = c.get("certificateId") or c.get("certificateId".lower()) or c.get("certificate_id") or c.get("_id") or "—"
            status = c.get("status", "—")
            created = c.get("createdAt") or c.get("created_at") or c.get("created") or None
            completed = c.get("completedAt") or c.get("completed_at") or None
            wipe_method = c.get("wipeMethod") or c.get("wipe_method") or (c.get("wipe") or {}).get("method") or "—"
            pdf = c.get("pdfUrl") or c.get("pdfurl") or c.get("pdf_url") or None

            def _fmt(ts):
                if not ts:
                    return "—"
                try:
                    # t may already be ISO or timestamp
                    if isinstance(ts, (int, float)):
                        return datetime.datetime.fromtimestamp(ts).isoformat(sep=" ", timespec="seconds")
                    # if string, try parse
                    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    return str(ts)

            gl.addWidget(QLabel("<b>ID:</b>"), 0, 0)
            gl.addWidget(QLabel(str(cert_id)), 0, 1)
            gl.addWidget(QLabel("<b>Status:</b>"), 1, 0)
            status_lbl = QLabel(status)
            status_lbl.setStyleSheet("color: #34d399; font-weight:600;" if status.lower() in ("passed","completed","success") else "color: #fca5a5; font-weight:600;")
            gl.addWidget(status_lbl, 1, 1)
            gl.addWidget(QLabel("<b>Created:</b>"), 2, 0)
            gl.addWidget(QLabel(_fmt(created)), 2, 1)
            gl.addWidget(QLabel("<b>Completed:</b>"), 3, 0)
            gl.addWidget(QLabel(_fmt(completed)), 3, 1)
            gl.addWidget(QLabel("<b>Method:</b>"), 4, 0)
            gl.addWidget(QLabel(wipe_method), 4, 1)
            gl.addWidget(QLabel("<b>PDF:</b>"), 5, 0)

            # PDF area with download button
            pdf_layout = QHBoxLayout()
            pdf_label = QLabel(pdf if pdf else "Not ready")
            pdf_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            pdf_layout.addWidget(pdf_label)
            if pdf:
                dl_btn = QPushButton("Download")
                dl_btn.setCursor(Qt.PointingHandCursor)
                dl_btn.setFixedHeight(28)
                dl_btn.setObjectName("primaryBtn")
                dl_btn.clicked.connect(lambda checked, url=pdf: webbrowser.open(url))
                pdf_layout.addWidget(dl_btn)

            gl.addLayout(pdf_layout, 5, 1)

            card.setLayout(gl)
            self.certs_layout.addWidget(card)

        self.certs_layout.addStretch()

    def _filter_certs(self):
        q = self.search_input.text().strip().lower()
        if not q:
            self._render_certificates(self.all_certs)
            return
        out = []
        for c in self.all_certs:
            s = ' '.join([str(v) for v in c.values() if v])
            if q in s.lower():
                out.append(c)
        self._render_certificates(out)


class WipeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureWipe — Desktop")
        self.resize(1000, 680)

        self._apply_global_styles()
        self._setup_ui()
        
        # Default to login page
        self.switch_page(0)

    def _setup_ui(self):
        # top-level layout
        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # header row (title + nav + status)
        header = QHBoxLayout()
        title = QLabel("🔐 SecureWipe")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #e2e8f0;")
        header.addWidget(title)

        # navbar buttons
        nav_row = QHBoxLayout()
        nav_row.setSpacing(10)
        self.btn_login_nav = QPushButton("Login")
        self.btn_wipe_nav = QPushButton("Wipe")
        self.btn_certs_nav = QPushButton("Certificates")

        for b in (self.btn_login_nav, self.btn_wipe_nav, self.btn_certs_nav):
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(36)
            b.setObjectName("navBtn")

        self.btn_login_nav.clicked.connect(lambda: self.switch_page(0))
        self.btn_wipe_nav.clicked.connect(lambda: self.switch_page(1))
        self.btn_certs_nav.clicked.connect(lambda: self.switch_page(2))

        nav_row.addWidget(self.btn_login_nav)
        nav_row.addWidget(self.btn_wipe_nav)
        nav_row.addWidget(self.btn_certs_nav)
        header.addLayout(nav_row)
        header.addStretch()

        # status area
        self.status_dot = StatusDot("#E53E3E")
        self.status_text = QLabel("Not signed in")
        self.status_text.setFont(QFont("Segoe UI", 10))
        self.status_text.setStyleSheet("color: #94a3b8;")
        status_box = QHBoxLayout()
        status_box.setSpacing(8)
        status_box.addWidget(self.status_dot, alignment=Qt.AlignVCenter)
        status_box.addWidget(self.status_text, alignment=Qt.AlignVCenter)
        header.addLayout(status_box)

        root.addLayout(header)

        # Stacked pages
        self.stack = QStackedWidget()
        
        # Create pages
        self.login_page = LoginPage()
        self.wipe_page = WipePage()
        self.certs_page = CertificatesPage()
        
        self.stack.addWidget(self.login_page)     # index 0
        self.stack.addWidget(self.wipe_page)      # index 1
        self.stack.addWidget(self.certs_page)     # index 2
        
        root.addWidget(self.stack, stretch=1)
        self.setLayout(root)

    def _apply_global_styles(self):
        self.setStyleSheet("""
            QWidget { background: #0f172a; font-family: "Segoe UI", Arial, sans-serif; color: #e2e8f0; }
            #card { background: #1e293b; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }
            QLabel { color: #e2e8f0; }
            QLineEdit, QComboBox {
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding-left: 8px;
                padding-right: 8px;
                color: #e2e8f0;
            }
            QPushButton#primaryBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0ea5e9, stop:1 #0284c7);
                color: white; border-radius: 8px; font-weight: 700;
            }
            QPushButton#primaryBtn:hover { background: #0284c7; }
            QPushButton#successBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #10b981, stop:1 #059669);
                color: white; border-radius: 8px; font-weight: 700;
            }
            QPushButton#navBtn { background: transparent; border-radius: 6px; padding: 6px 12px; color: #94a3b8; }
            QPushButton#navBtn:hover { background: rgba(14,165,233,0.06); }
            QScrollArea { border: none; }
            QProgressBar { background: #334155; border-radius: 8px; height: 14px; }
            QProgressBar::chunk { border-radius: 8px; background-color: #0ea5e9; }
            QListWidget { background: #0f172a; border: 1px solid #334155; border-radius: 8px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #334155; }
            QListWidget::item:selected { background: #1e40af; }
            QListWidget::item:hover { background: #1e3a8a; }
            QDialog { background: #0f172a; }
        """)
        p = self.palette()
        p.setColor(QPalette.Window, QColor("#0f172a"))
        self.setPalette(p)

    def switch_page(self, idx: int):
        self.stack.setCurrentIndex(idx)
        # simple nav highlight (bold the active nav button)
        for btn, i in ((self.btn_login_nav, 0), (self.btn_wipe_nav, 1), (self.btn_certs_nav, 2)):
            if i == idx:
                btn.setProperty("active", True)
                btn.setStyleSheet("font-weight: 700; color: #e2e8f0;")
            else:
                btn.setProperty("active", False)
                btn.setStyleSheet("font-weight: 400; color: #94a3b8;")

    def update_status(self, authenticated=False):
        """Update the status indicator"""
        if authenticated:
            self.status_dot.setStyleSheet("border-radius:6px; background:#10b981;")
            self.status_text.setText("Signed in")
            self.wipe_page.enable_wipe_button(True)
        else:
            self.status_dot.setStyleSheet("border-radius:6px; background:#E53E3E;")
            self.status_text.setText("Not signed in")
            self.wipe_page.enable_wipe_button(False)

    def show_message(self, title, message, msg_type="info"):
        """Show message box"""
        if msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def show_drive_selection_dialog(self, drives):
        """Show drive selection dialog and return selected path"""
        dialog = DriveSelectionDialog(drives, self)
        if dialog.exec() == QDialog.Accepted:
            return dialog.selected_path
        return None