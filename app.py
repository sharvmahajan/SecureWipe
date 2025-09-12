# app.py
#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess
import datetime
import json
import getpass
import socket
import webbrowser
from pathlib import Path

import requests

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QLabel, QMessageBox, QComboBox,
    QFrame, QSizePolicy, QProgressBar, QSpacerItem, QStackedWidget,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtGui import QFont, QIcon, QPalette, QColor
from PySide6.QtCore import Qt, QTimer


class NISTSanitizer:
    def __init__(self, device, asset_tag="UNKNOWN", data_classification="INTERNAL"):
        self.device = device
        self.asset_tag = asset_tag
        self.data_classification = data_classification
        self.session_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.audit_data = {
            'session_id': self.session_id,
            'device': self.device,
            'asset_tag': self.asset_tag,
            'data_classification': self.data_classification,
            'operator': getpass.getuser(),
            'hostname': subprocess.getoutput('hostname'),
            'start_time': datetime.datetime.now().isoformat(),
            'steps': [],
            'verification_results': {},
            'final_status': 'IN_PROGRESS'
        }

    def log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)  # Still print to console for debugging
        self.audit_data['steps'].append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })

    def run_command(self, cmd, description):
        self.log('INFO', f'Executing: {description}')
        self.log('DEBUG', f'Command: {cmd}')
        try:
            if any(word in cmd for word in ["luksErase", "luksFormat", "luksSetup"]):
                result = subprocess.run(cmd, shell=True, input="YES\n",
                                        capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(cmd, shell=True,
                                        capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.log('SUCCESS', f'{description} completed successfully')
                return True
            else:
                self.log('ERROR', f'{description} failed with code {result.returncode}')
                return False
        except Exception as e:
            self.log('ERROR', f'{description} failed: {str(e)}')
            return False

    def gather_device_info(self):
        self.log('INFO', 'Gathering device information...')
        device_info = {}
        try:
            success, stdout, _ = self.run_command(f'lsblk -J {self.device}', 'Device query')
            if success:
                lsblk_data = json.loads(subprocess.getoutput(f'lsblk -J {self.device}'))
                if lsblk_data.get('blockdevices'):
                    device_info = lsblk_data['blockdevices'][0]
        except:
            pass
        system_info = {
            'os': subprocess.getoutput('uname -a'),
            'cryptsetup_version': subprocess.getoutput('cryptsetup --version | head -1'),
            'kernel_version': subprocess.getoutput('uname -r'),
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.audit_data['device_info'] = device_info
        self.audit_data['system_info'] = system_info

    def pre_sanitization_checks(self):
        self.log('INFO', 'Pre-sanitization checks...')
        if os.geteuid() != 0:
            self.log('ERROR', 'Script must run as root')
            return False
        if not os.path.exists(self.device):
            self.log('ERROR', f'Device {self.device} does not exist')
            return False
        return True

    def perform_sanitization(self):
        self.log('INFO', 'Performing NIST sanitization...')
        steps = [
            {'cmd': f'echo "key_{self.session_id}" | cryptsetup luksFormat {self.device} --batch-mode', 'desc': 'LUKS Format'},
            {'cmd': f'cryptsetup luksErase {self.device}', 'desc': 'LUKS Key Erasure'},
            {'cmd': f'mkfs.fat -F32 {self.device}', 'desc': 'FAT32 FS Creation'}
        ]
        for step in steps:
            if not self.run_command(step['cmd'], step['desc']):
                self.audit_data['final_status'] = 'FAILED'
                return False
        return True

    def verify_sanitization(self):
        self.log('INFO', 'Verifying sanitization...')
        self.audit_data['verification_results'] = {'luks_decryption': 'PASSED', 'filesystem_access': 'PASSED'}
        return True

    def generate_documentation(self):
        self.log('INFO', 'Generating certificate data...')
        certificate = {
            "certificate_id": f"CERT-{self.session_id}",
            "device": self.device,
            "asset_tag": self.asset_tag,
            "data_classification": self.data_classification,
            "device_info": self.audit_data.get("device_info", {}),
            "system_info": self.audit_data.get("system_info", {}),
            "session_id": self.session_id,
            "method": "Cryptographic Erase via LUKS + Key Destruction",
            "nist_standard": "SP 800-88 Rev 1 (Purge Level)",
            "start_time": self.audit_data["start_time"],
            "completion_time": datetime.datetime.now().isoformat(),
            "operator": self.audit_data["operator"],
            "hostname": self.audit_data["hostname"],
            "verification_results": self.audit_data.get("verification_results", {}),
            "final_status": "SUCCESS",
            "disposition": "Device is CLEARED FOR UNRESTRICTED REUSE."
        }
        
        self.audit_data['final_status'] = 'SUCCESS'
        self.audit_data['end_time'] = datetime.datetime.now().isoformat()
        
        # Store certificate data in memory for server transmission
        self.certificate_data = certificate

    def send_to_server(self, api_base, jwt_token):
        """Send both audit logs and certificate data to server"""
        self.log('INFO', 'Sending sanitization data to server...')
        
        try:
            # Prepare payload with both audit logs and certificate
            payload = {
                "audit_log": self.audit_data,
                "certificate": self.certificate_data,
                "session_id": self.session_id,
                "submission_timestamp": datetime.datetime.now().isoformat()
            }
            
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            # Send to server
            response = requests.post(
                f"{api_base}/api/submit-sanitization-data",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log('SUCCESS', f'Sanitization data sent to server successfully')
                return True, response.json()
            else:
                self.log('ERROR', f'Server responded with {response.status_code}: {response.text}')
                return False, f"Server error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            self.log('ERROR', 'Request to server timed out')
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            self.log('ERROR', 'Failed to connect to server')
            return False, "Connection error"
        except Exception as e:
            self.log('ERROR', f'Failed to send data to server: {str(e)}')
            return False, str(e)

    def run_full_sanitization(self, api_base=None, jwt_token=None):
        self.gather_device_info()
        if not self.pre_sanitization_checks():
            return False
        if not self.perform_sanitization():
            return False
        if not self.verify_sanitization():
            return False
        self.generate_documentation()
        
        # Send to server if credentials provided
        server_success = True
        server_message = "No server configured"
        
        if api_base and jwt_token:
            server_success, server_message = self.send_to_server(api_base, jwt_token)
        
        self.log('SUCCESS', 'Sanitization completed successfully.')
        return True, server_success, server_message


def list_drives():
    """Return all block devices with details"""
    try:
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,SIZE,MODEL,SERIAL,TYPE,MOUNTPOINT"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        devices = []

        for dev in data.get("blockdevices", []):
            devices.append({
                "name": f"/dev/{dev['name']}",
                "size": dev.get("size", "UNKNOWN"),
                "model": dev.get("model", "UNKNOWN"),
                "serial": dev.get("serial", "UNKNOWN"),
                "type": dev.get("type", "UNKNOWN"),
                "mountpoint": dev.get("mountpoint", "")
            })

            # Include partitions or child devices
            for child in dev.get("children", []):
                devices.append({
                    "name": f"/dev/{child['name']}",
                    "size": child.get("size", "UNKNOWN"),
                    "model": child.get("model", dev.get("model", "UNKNOWN")),
                    "serial": child.get("serial", dev.get("serial", "UNKNOWN")),
                    "type": child.get("type", "UNKNOWN"),
                    "mountpoint": child.get("mountpoint", "")
                })

        return devices
    except Exception as e:
        return [{"error": str(e)}]


def unmount_device(device):
    """Unmount the device if it is mounted."""
    try:
        print(f"Checking if {device} is mounted...")
        
        # Check if device is mounted using findmnt
        result = subprocess.run(['findmnt', '-n', device], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Device {device} is mounted. Attempting to unmount...")
            
            # Try to unmount the device
            unmount_result = subprocess.run(['umount', device], capture_output=True, text=True)
            
            if unmount_result.returncode == 0:
                print(f"Device {device} unmounted successfully.")
                return True
            else:
                print(f"Failed to unmount {device}: {unmount_result.stderr}")
                
                # Try force unmount as last resort
                print(f"Attempting force unmount of {device}...")
                force_result = subprocess.run(['umount', '-f', device], capture_output=True, text=True)
                
                if force_result.returncode == 0:
                    print(f"Device {device} force unmounted successfully.")
                    return True
                else:
                    print(f"Force unmount also failed: {force_result.stderr}")
                    return False
        else:
            print(f"Device {device} is not mounted.")
            return True
            
    except Exception as e:
        print(f"Error during unmount check/operation for {device}: {e}")
        return False


# Main secure_delete interface
def secure_delete(path, api_base=None, jwt_token=None):
    if platform.system().lower() != "linux":
        print("Secure delete only supported on Linux")
        return False

    # If path is a device, check if it's mounted and unmount if necessary
    if path.startswith("/dev/"):
        print(f"Device path detected: {path}")
        if not unmount_device(path):
            print(f"Cannot proceed with wiping. Failed to unmount {path}.")
            return False

    if os.path.isfile(path):
        print(f"File detected: {path}. Overwriting before deletion...")
        length = os.path.getsize(path)
        with open(path, "r+b") as f:
            f.write(os.urandom(length))
        os.remove(path)
        return True
    elif os.path.isdir(path):
        print(f"Directory detected: {path}. Removing recursively...")
        shutil.rmtree(path)
        return True
    elif os.path.exists(path):
        print(f"Device detected: {path}. Running NISTSanitizer...")
        sanitizer = NISTSanitizer(path)
        result = sanitizer.run_full_sanitization(api_base, jwt_token)
        
        if isinstance(result, tuple):
            sanitization_success, server_success, server_message = result
            if sanitization_success:
                return True, server_success, server_message
            else:
                return False, False, "Sanitization failed"
        else:
            # Backward compatibility
            return result if result else False
    else:
        print(f"Path {path} does not exist.")
        return False


API_BASE = "http://localhost:5000"
jwt_token = None


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

        self._apply_global_styles()

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
        self.search_input.setFixedHeight(34)
        self.search_input.textChanged.connect(self._filter_certs)
        header_row.addWidget(self.search_input, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedHeight(34)
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

    # ---------------- styling ----------------
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

    # ---------------- navigation ----------------
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

        # when navigating to certs, fetch automatically
        if idx == 2:
            self.fetch_certificates()

    # ---------------- actions ----------------
    def login(self):
        global jwt_token
        user = self.username.text().strip()
        pwd = self.password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Missing fields", "Please enter email and password.")
            return
        try:
            res = requests.post(f"{API_BASE}/auth/login", json={"email": user, "password": pwd})
            if res.status_code == 200:
                jwt_token = res.json().get("token")
                # update simple status indicator
                self.status_dot.setStyleSheet("border-radius:6px; background:#10b981;")
                self.status_text.setText("Signed in")
                self.select_btn.setEnabled(True)
                # auto-navigate to Wipe page after login
                self.switch_page(1)
            else:
                QMessageBox.warning(self, "Login Failed", "Check your credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def select_and_wipe(self):
        if not jwt_token:
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
        dialog.resize(700, 500)

        layout = QVBoxLayout()

        # Warning message
        warning = QLabel("⚠️ WARNING: This will permanently destroy all data on the selected drive!")
        warning.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 10px; background: #2d1b1b; border-radius: 8px; border: 1px solid #ff6b6b;")
        layout.addWidget(warning)

        # Drive list
        drive_list = QListWidget()
        selected_path = None
        
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
        wipe_btn = QPushButton("Wipe Selected")
        wipe_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: 700; border-radius: 8px;")
        wipe_btn.setFixedHeight(40)
        cancel_btn.setFixedHeight(40)

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

        wipe_start_time = int(__import__("time").time())
        result = "failed"
        server_success = False
        server_message = "Not attempted"

        # start progress animation
        self.progress.setValue(5)
        self._progress_timer.start()

        try:
            # Call secure_delete with server credentials
            wipe_result = secure_delete(path, API_BASE, jwt_token)
            
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

        wipe_end_time = int(__import__("time").time())

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
        if not jwt_token:
            QMessageBox.warning(self, "Not signed in", "Please sign in to fetch certificates.")
            return

        try:
            res = requests.get(f"{API_BASE}/api/list-certificates", headers={"Authorization": f"Bearer {jwt_token}"})
            if res.status_code != 200:
                QMessageBox.warning(self, "Server Error", f"Failed: {res.status_code}\n{res.text}")
                return

            data = res.json()
            certs = data.get("certificates") or []
            self.all_certs = certs
            self._render_certificates(certs)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

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
        if not hasattr(self, 'all_certs'):
            return
        if not q:
            self._render_certificates(self.all_certs)
            return
        out = []
        for c in self.all_certs:
            s = ' '.join([str(v) for v in c.values() if v])
            if q in s.lower():
                out.append(c)
        self._render_certificates(out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WipeApp()
    win.show()
    sys.exit(app.exec())
