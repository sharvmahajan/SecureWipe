#!/usr/bin/env python3
"""
SecureWipe Desktop Application
Main entry point for the application
"""
import sys
from PySide6.QtWidgets import QApplication

from ui_components import WipeApp


def main():
    """Main application entry point"""
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("SecureWipe")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SecureWipe Inc.")
    
    # Create and show the main window
    window = WipeApp()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()