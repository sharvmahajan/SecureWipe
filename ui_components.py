#!/usr/bin/env python3
import os
import sys
import json
import datetime
import webbrowser
import time

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QComboBox,
    QFrame, QSizePolicy, QProgressBar, QSpacerItem, QStackedWidget,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QTimer

from business_logic import APIClient, list_drives, secure_delete


class StatusDot(QLabel):
    """Small colored dot used for status indicators."""
    def __init__(self, color="#d0d0d0", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setStyleSheet(f"border-radius:6px; background:{color};")


class WipeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureWipe — Desktop")
        self.resize(1000, 680)
        
        # Initialize API client
        self.api_client = APIClient("https://express-server-production-b4f4.up.railway.app")
        
        # Store certificates for filtering
        self.all_certs = []

        self._apply_global_styles()

        # top-level layout
        root = QVBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # header row (title + nav + status)
        header = QHBoxLayout()
        title = QLabel("🔐 SecureWipe")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #e6eef8;")
        header.addWidget(title)

        # navbar buttons
        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)
        self.btn_login_nav = QPushButton("Login")
        self.btn_wipe_nav = QPushButton("Wipe")
        self.btn_certs_nav = QPushButton("Certificates")
        self.btn_verify_nav = QPushButton("Verify")

        for b in (self.btn_login_nav, self.btn_wipe_nav, self.btn_certs_nav, self.btn_verify_nav):
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(34)
            b.setObjectName("navBtn")

        self.btn_login_nav.clicked.connect(lambda: self.switch_page(0))
        self.btn_wipe_nav.clicked.connect(lambda: self.switch_page(1))
        self.btn_certs_nav.clicked.connect(lambda: self.switch_page(2))
        self.btn_verify_nav.clicked.connect(lambda: self.switch_page(3))

        nav_row.addWidget(self.btn_login_nav)
        nav_row.addWidget(self.btn_wipe_nav)
        nav_row.addWidget(self.btn_certs_nav)
        nav_row.addWidget(self.btn_verify_nav)
        header.addLayout(nav_row)
        header.addStretch()

        # status area (keeps simple status indicator, not a sign-in bar)
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
        self.stack.addWidget(self._build_login_page())     # index 0
        self.stack.addWidget(self._build_wipe_page())      # index 1
        self.stack.addWidget(self._build_certs_page())     # index 2
        self.stack.addWidget(self._build_verify_page())    # index 3
        root.addWidget(self.stack, stretch=1)

        self.setLayout(root)

        # progress timer for wipe progress simulation
        self._progress_timer = QTimer()
        self._progress_timer.setInterval(30)
        self._progress_timer.timeout.connect(self._advance_progress)

        # default to login page
        self.switch_page(0)

    # ---------------- UI builders ----------------
    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        lbl = QLabel("Sign in to your account")
        lbl.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
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
        self.login_btn.setFixedHeight(38)
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.clicked.connect(self.login)
        card_layout.addWidget(self.login_btn)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignTop)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _build_wipe_page(self):
        page = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(16)

        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        wipe_card = QFrame()
        wipe_card.setObjectName("card")
        wipe_card_layout = QVBoxLayout()
        wipe_card_layout.setContentsMargins(16, 16, 16, 16)
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
        actions.setSpacing(12)
        self.select_btn = QPushButton("Select drive & wipe")
        self.select_btn.setEnabled(False)
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.setObjectName("successBtn")
        self.select_btn.setFixedHeight(40)
        self.select_btn.clicked.connect(self.select_and_wipe)
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
            "<div style='font-size:14px;color:#e6eef8;'>"
            "<b>SecureWipe</b><br>"
            "<span style='color:#9fb0c8'>Fast, verifiable secure deletions</span><br><br>"
            "<span style='color:#b9c9d9;font-size:11px'>"
            "• Wipe methods: zero / random / DoD<br>"
            "• Server-signed certificates and PDFs<br>"
            "• Cloud upload for signed certificates"
            "</span></div>"
        )
        info.setAlignment(Qt.AlignTop)
        right_col.addWidget(info)
        right_col.addStretch()
        layout.addLayout(right_col, 1)

        page.setLayout(layout)
        return page

    def _build_certs_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_label = QLabel("Certificates")
        header_label.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        header_row.addWidget(header_label)
        header_row.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, status or method...")
        self.search_input.setFixedHeight(36)
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self._filter_certs)
        header_row.addWidget(self.search_input, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedHeight(36)
        refresh_btn.setObjectName("primaryBtn")
        refresh_btn.clicked.connect(self.fetch_certificates)
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

        page.setLayout(layout)
        return page

    def _build_verify_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        title = QLabel("Verify")
        title.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        card_layout.addWidget(title)

        subtitle = QLabel("Open the verification portal to check a certificate.")
        subtitle.setProperty("role", "muted")
        card_layout.addWidget(subtitle)

        btn = QPushButton("Open Verification Portal")
        btn.setObjectName("primaryBtn")
        btn.setFixedHeight(38)
        btn.clicked.connect(lambda: webbrowser.open("https://next-frontend-nu-two.vercel.app/verify"))
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignTop)
        layout.addStretch()
        page.setLayout(layout)
        return page

    # ---------------- styling ----------------
    def _apply_global_styles(self):
        # Modern, consistent visual theme. Buttons are centralized by objectName so code doesn't need inline styles.
        self.setStyleSheet("""
            /* App background and base text */
            QWidget { background: #071025; font-family: "Segoe UI", Arial, sans-serif; color: #e6eef8; }
           
            /* Generic card */
            QFrame#card {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0b2236, stop:1 #071025);
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.04);
            }

            /* Certificate card specifically */
            QFrame#certCard, QFrame[objectName="card"] {
                background: #071025;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.04);
                padding: 12px;
            }

            /* Labels */
            QLabel { color: #dbe9f7; }
            QLabel[role="muted"] { color: #9fb0c8; font-size: 12px; }

            /* Inputs */
            QLineEdit#searchInput {
                background: #0b2a44;
                border: 1px solid #133a56;
                border-radius: 8px;
                padding: 6px 10px;
                color: #e6eef8;
            }
            QLineEdit, QComboBox {
                background: #071a2d;
                border: 1px solid #133a56;
                border-radius: 8px;
                padding-left: 8px;
                padding-right: 8px;
                color: #e6eef8;
                min-height: 34px;
            }

            /* Nav buttons */
            QPushButton#navBtn {
                background: transparent;
                color: #9fb0c8;
                padding: 6px 12px;
                border-radius: 8px;
                border: none;
                font-weight: 600;
            }
            QPushButton#navBtn[active="true"] {
                color: #e6eef8;
                background: rgba(14,165,233,0.12);
            }

            /* Primary button (blue) */
            QPushButton#primaryBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0ea5e9, stop:1 #0284c7);
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 700;
                min-height: 36px;
            }

            /* Success button (green) */
            QPushButton#successBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #10b981, stop:1 #059669);
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 700;
                min-height: 36px;
            }

            /* Danger button (red) */
            QPushButton#dangerBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff6b6b, stop:1 #f43f5e);
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 700;
                min-height: 36px;
            }

            /* Ghost / subtle button */
            QPushButton#ghostBtn {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.04);
                color: #cfe6fb;
                border-radius: 8px;
                padding: 6px 12px;
                min-height: 36px;
            }

            /* Download specialized button */
            QPushButton#downloadBtn {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
                min-height: 34px;
            }

            /* Progress bar */
            QProgressBar { background: #072033; border-radius: 8px; height: 14px; border: 1px solid #133a56; }
            QProgressBar::chunk { border-radius: 8px; background-color: #0ea5e9; }

            /* Scroll area tweaks */
            QScrollArea { border: none; }
        """)
        p = self.palette()
        p.setColor(QPalette.Window, QColor("#071025"))
        self.setPalette(p)

    # ---------------- navigation ----------------
    def switch_page(self, idx: int):
        self.stack.setCurrentIndex(idx)
        # simple nav highlight (bold the active nav button)
        for btn, i in (
            (self.btn_login_nav, 0),
            (self.btn_wipe_nav, 1),
            (self.btn_certs_nav, 2),
            (self.btn_verify_nav, 3),
        ):
            if i == idx:
                btn.setProperty("active", True)
                btn.setProperty("active", "true")
                btn.setStyleSheet("")
            else:
                btn.setProperty("active", False)
                btn.setProperty("active", "false")
                btn.setStyleSheet("")

        # when navigating to certs, fetch automatically
        if idx == 2:
            self.fetch_certificates()

    # ---------------- actions ----------------
    def login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Missing fields", "Please enter email and password.")
            return
        
        success, result = self.api_client.login(user, pwd)
        if success:
            # update simple status indicator
            self.status_dot.setStyleSheet("border-radius:6px; background:#10b981;")
            self.status_text.setText("Signed in")
            self.select_btn.setEnabled(True)
            # auto-navigate to Wipe page after login
            self.switch_page(1)
        else:
            QMessageBox.warning(self, "Login Failed", result)

    def select_and_wipe(self):
        if not self.api_client.jwt_token:
            QMessageBox.warning(self, "Not signed in", "Please sign in before starting a wipe.")
            return

        # Get available drives
        drives = list_drives()
       
        if not drives or (len(drives) == 1 and 'error' in drives[0]):
            QMessageBox.critical(self, "Error", "Cannot retrieve drive list. Make sure you have proper permissions.")
            return

        # Create drive selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Drive to Wipe")
        dialog.setModal(True)
        dialog.resize(740, 520)

        layout = QVBoxLayout()

        # Warning message
        warning = QLabel("⚠️ WARNING: This will permanently destroy all data on the selected drive!")
        warning.setStyleSheet("color: #ffb4b4; font-weight: 700; padding: 10px; background: rgba(244,63,94,0.06); border-radius: 8px;")
        layout.addWidget(warning)

        # Drive list
        drive_list = QListWidget()
        drive_list.setStyleSheet("background: #071025; border: 1px solid #133a56; border-radius: 8px;")
       
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
            drive_list.addItem(item)

        layout.addWidget(QLabel("Available drives:"))
        layout.addWidget(drive_list)

        # Option to select file/folder instead
        file_folder_btn = QPushButton("Select File/Folder Instead")
        file_folder_btn.setObjectName("primaryBtn")
        file_folder_btn.setFixedHeight(36)
        layout.addWidget(file_folder_btn)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghostBtn")
        cancel_btn.setFixedHeight(36)
        wipe_btn = QPushButton("Wipe Selected")
        wipe_btn.setObjectName("dangerBtn")
        wipe_btn.setFixedHeight(36)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(wipe_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        cancel_btn.clicked.connect(dialog.reject)

        def on_file_folder_select():
            dialog.accept()
            path = QFileDialog.getExistingDirectory(self, "Select Folder to Wipe")
            if path:
                self.perform_wipe(path)

        def on_wipe():
            current_item = drive_list.currentItem()
            if not current_item:
                QMessageBox.warning(dialog, "No Selection", "Please select a drive to wipe.")
                return
               
            drive_path = current_item.data(Qt.UserRole)
           
            # Final confirmation
            reply = QMessageBox.question(
                dialog,
                "Final Confirmation",
                f"Are you absolutely sure you want to wipe {drive_path}?\n\nThis action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
           
            if reply == QMessageBox.Yes:
                dialog.accept()
                self.perform_wipe(drive_path)

        file_folder_btn.clicked.connect(on_file_folder_select)
        wipe_btn.clicked.connect(on_wipe)

        dialog.exec()

    def perform_wipe(self, path):
        """Perform the actual wiping process"""
        method = self.method_box.currentText()
        policy = self.policy_box.currentText()

        try:
            capacity_gb = int(self.capacity_input.text().strip()) if self.capacity_input.text().strip() else 0
        except ValueError:
            capacity_gb = 0

        result = "failed"
        server_success = False
        server_message = "Not attempted"

        # start progress animation
        self.progress.setValue(5)
        self._progress_timer.start()

        try:
            # Call secure_delete with server credentials
            wipe_result = secure_delete(path, self.api_client.api_base, self.api_client.jwt_token)
           
            if isinstance(wipe_result, tuple):
                # Device wiping with server transmission
                sanitization_success, server_success, server_message = wipe_result
                if sanitization_success:
                    result = "passed"
            else:
                # File/folder wiping (boolean result)
                if wipe_result:
                    result = "passed"
                   
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Wipe failed: {str(e)}")
            result = "failed"

        # stop animation quickly and set to complete
        self._progress_timer.stop()
        self.progress.setValue(100)

        # Display results based on wipe status and server communication
        if result == "passed":
            if server_success:
                QMessageBox.information(self, "Success",
                    f"Wipe completed successfully\n"
                    f"• Audit logs and certificate sent to server")
            else:
                QMessageBox.information(self, "Partial Success",
                    f"Wipe completed successfully\n"
                    f"• Server communication failed: {server_message}")
        else:
            QMessageBox.critical(self, "Wipe Failed",
                "The wiping process failed. Check logs for details.")

        # reset progress slowly
        QTimer.singleShot(600, lambda: self.progress.setValue(0))

    def _advance_progress(self):
        v = self.progress.value()
        if v < 95:
            self.progress.setValue(v + 2)
        else:
            self.progress.setValue(95)

    # ---------------- certificates fetch & render ----------------
    def fetch_certificates(self):
        if not self.api_client.jwt_token:
            QMessageBox.warning(self, "Not signed in", "Please sign in to fetch certificates.")
            return

        success, result = self.api_client.fetch_certificates()
        if success:
            self.all_certs = result
            self._render_certificates(result)
        else:
            QMessageBox.warning(self, "Server Error", result)

    def _render_certificates(self, certs):
        # clear old items
        for i in reversed(range(self.certs_layout.count())):
            item = self.certs_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not certs:
            lbl = QLabel("No certificates found.")
            lbl.setStyleSheet("color: #9fb0c8; font-size: 13px;")
            self.certs_layout.addWidget(lbl)
            self.certs_layout.addStretch()
            return

        def _fmt(ts):
            if not ts:
                return "—"
            try:
                return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return str(ts)

        for c in certs:
            card = QFrame()
            card.setObjectName("certCard")
            card.setStyleSheet("")
            gl = QGridLayout()
            gl.setSpacing(8)

            payload = c.get("payload") or {}
            cert_num = c.get("certificateId") or payload.get("certificate_id", "—")
            session_id = payload.get("session_id", "—")
            nist_std = payload.get("nist_standard", "—")
            start_time = payload.get("start_time")
            method = payload.get("method", "—")
            disposition = payload.get("disposition", "—")

            # Certificate ID
            label_id = QLabel("<b>Certificate ID:</b>")
            label_id.setProperty("role", "muted")
            gl.addWidget(label_id, 0, 0)
            cid_lbl = QLabel(cert_num)
            cid_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            cid_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            gl.addWidget(cid_lbl, 0, 1)

            # Session ID
            gl.addWidget(QLabel("<b>Session ID:</b>"), 1, 0)
            gl.addWidget(QLabel(session_id), 1, 1)

            # NIST standard
            gl.addWidget(QLabel("<b>NIST Standard:</b>"), 2, 0)
            gl.addWidget(QLabel(nist_std), 2, 1)

            # Start time
            gl.addWidget(QLabel("<b>Start Time:</b>"), 3, 0)
            gl.addWidget(QLabel(_fmt(start_time)), 3, 1)

            # Method
            gl.addWidget(QLabel("<b>Method:</b>"), 4, 0)
            gl.addWidget(QLabel(method), 4, 1)

            # Disposition
            gl.addWidget(QLabel("<b>Disposition:</b>"), 5, 0)
            disp_lbl = QLabel(disposition)
            disp_lbl.setWordWrap(True)
            gl.addWidget(disp_lbl, 5, 1)

            # Download button
            download_btn = QPushButton("Download PDF")
            download_btn.setCursor(Qt.PointingHandCursor)
            download_btn.setFixedHeight(34)
            download_btn.setObjectName("downloadBtn")
            download_btn.clicked.connect(lambda _, cid=cert_num: self.download_certificate(cid))

            btn_row = QHBoxLayout()
            btn_row.addStretch()
            btn_row.addWidget(download_btn)
            gl.addLayout(btn_row, 6, 0, 1, 2)

            card.setLayout(gl)
            self.certs_layout.addWidget(card)

        self.certs_layout.addStretch()

    def download_certificate(self, cert_id: str):
        """Download certificate PDF from API and prompt user to save it locally."""
        if not cert_id or cert_id == "—":
            QMessageBox.warning(self, "Invalid Certificate", "Certificate ID not available for download.")
            return

        success, result = self.api_client.download_certificate(cert_id)
        if success:
            # Ask user where to save
            default_name = f"certificate_{cert_id}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "Save Certificate", default_name, "PDF Files (*.pdf)")
            if path:
                try:
                    with open(path, "wb") as f:
                        for chunk in result.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    QMessageBox.information(self, "Download Complete", f"Certificate saved to {path}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")
        else:
            QMessageBox.warning(self, "Download Failed", result)

    def _filter_certs(self):
        q = self.search_input.text().strip().lower()
        if not hasattr(self, 'all_certs'):
            return
        if not q:
            self._render_certificates(self.all_certs)
            return
        out = []
        for c in self.all_certs:
            try:
                s = json.dumps(c).lower()
            except Exception:
                s = str(c).lower()
            if q in s:
                out.append(c)
        self._render_certificates(out)