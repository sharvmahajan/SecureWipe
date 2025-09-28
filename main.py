#!/usr/bin/env python3
import sys
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from business_logic import APIManager, DriveManager, SecureDeleteManager
from ui_components import WipeApp


class SecureWipeApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = WipeApp()
        self.api_manager = APIManager("http://localhost:5000")
        
        self._connect_signals()
        
    def _connect_signals(self):
        """Connect UI signals to business logic handlers"""
        # Login page signals
        self.ui.login_page.login_requested.connect(self._handle_login)
        
        # Wipe page signals
        self.ui.wipe_page.wipe_requested.connect(self._handle_wipe_request)
        
        # Certificates page signals
        self.ui.certs_page.refresh_requested.connect(self._handle_refresh_certificates)
        
    def _handle_login(self, email, password):
        """Handle login request from UI"""
        success, message = self.api_manager.login(email, password)
        
        if success:
            self.ui.update_status(authenticated=True)
            self.ui.login_page.clear_fields()
            # Auto-navigate to Wipe page after successful login
            self.ui.switch_page(1)
        else:
            self.ui.show_message("Login Failed", message, "error")
    
    def _handle_wipe_request(self, request_type):
        """Handle wipe request from UI"""
        if not self.api_manager.is_authenticated():
            self.ui.show_message("Not signed in", "Please sign in before starting a wipe.", "warning")
            return
        
        if request_type == "select_drive":
            self._select_and_wipe_drive()
    
    def _select_and_wipe_drive(self):
        """Handle drive selection and wiping process"""
        # Get available drives
        drives = DriveManager.list_drives()
        
        if not drives or (len(drives) == 1 and 'error' in drives[0]):
            self.ui.show_message("Error", "Cannot retrieve drive list. Make sure you have proper permissions.", "error")
            return
        
        # Show drive selection dialog
        selected_path = self.ui.show_drive_selection_dialog(drives)
        
        if selected_path:
            self._perform_wipe(selected_path)
    
    def _perform_wipe(self, path):
        """Perform the actual wiping process"""
        wipe_config = self.ui.wipe_page.get_wipe_config()
        
        # Start progress animation
        self.ui.wipe_page.start_progress()
        
        try:
            # Call secure_delete with server credentials
            wipe_result = SecureDeleteManager.secure_delete(
                path, 
                self.api_manager.api_base, 
                self.api_manager.get_token()
            )
            
            # Process results
            result = "failed"
            server_success = False
            server_message = "Not attempted"
            
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
            self.ui.show_message("Error", f"Wipe failed: {str(e)}", "error")
            result = "failed"
            server_success = False
            server_message = str(e)
        
        # Stop progress animation
        self.ui.wipe_page.stop_progress()
        
        # Display results based on wipe status and server communication
        if result == "passed":
            if server_success:
                self.ui.show_message("Success", 
                    "Wipe completed successfully\n"
                    "• Audit logs and certificate sent to server")
            else:
                self.ui.show_message("Partial Success", 
                    f"Wipe completed successfully\n"
                    f"• Server communication failed: {server_message}", 
                    "warning")
        else:
            self.ui.show_message("Wipe Failed", 
                "The wiping process failed. Check logs for details.", 
                "error")
    
    def _handle_refresh_certificates(self):
        """Handle certificate refresh request from UI"""
        if not self.api_manager.is_authenticated():
            self.ui.show_message("Not signed in", "Please sign in to fetch certificates.", "warning")
            return
        
        success, data = self.api_manager.get_certificates()
        
        if success:
            certificates = data if isinstance(data, list) else []
            self.ui.certs_page.update_certificates(certificates)
        else:
            self.ui.show_message("Server Error", f"Failed to fetch certificates: {data}", "error")
    
    def run(self):
        """Start the application"""
        self.ui.show()
        
        # Auto-refresh certificates when navigating to certificates page
        def on_page_change():
            if self.ui.stack.currentIndex() == 2:  # Certificates page
                QTimer.singleShot(100, self._handle_refresh_certificates)
        
        # Connect to page changes (this is a bit of a workaround since QStackedWidget doesn't have a signal)
        self.ui.btn_certs_nav.clicked.connect(on_page_change)
        
        return self.app.exec()


if __name__ == "__main__":
    app = SecureWipeApplication()
    sys.exit(app.run())