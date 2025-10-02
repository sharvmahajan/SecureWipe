# DELTON Desktop Application – Modular Components

This folder contains the modular components for the DELTON Enterprise Desktop Application, an enterprise-grade platform for secure data sanitization, certificate management, and ML-based drive health checks.

## Contents

- **ui_components.py**  
  All PySide6-based UI classes and the main application window.  
  Includes navigation, authentication, ML health check, secure wipe, certificate management, verification, and settings.

- **main.py**  
  Application entry point. Instantiates and runs the DELTONApp from `ui_components.py`.

- **business_logic.py**  
  Core logic for wiping, health checks, API communication, and certificate management.

## Requirements

- Python 3.8+
- [PySide6](https://pypi.org/project/PySide6/)
- [requests](https://pypi.org/project/requests/)

Install dependencies:
```sh
pip install PySide6 requests
```

## Usage

Run the application:
```sh
python main.py
```

## Features

- **Modern UI/UX:** Professional interface with dark/light themes
- **Secure Data Wiping:** NIST, DoD, and custom methods
- **ML Health Check:** Analyze drive health using machine learning
- **Certificate Management:** View, download, and verify certificates
- **Comprehensive Logging:** Activity logs and audit trails
- **Settings:** Customizable appearance, security, and advanced options

## Creating an Executable

You can package the application as a standalone executable using [PyInstaller](https://pyinstaller.org/):

1. Install PyInstaller:
    ```sh
    pip install pyinstaller
    ```

2. Build the executable (recommended flags for a GUI app):
    ```sh
    pyinstaller --onefile --noconsole main.py
    ```

   - `--onefile` creates a single executable.
   - `--noconsole` prevents a terminal window from opening (for GUI apps).

3. The executable will be available in the `dist` folder.

## WebApp

- **Website Frontend:** [https://github.com/bzubs/next-frontend](https://github.com/bzubs/next-frontend)
- **Website Backend:** [https://github.com/bzubs/express-server](https://github.com/bzubs/express-server)
---
## License

© DELTON Inc. All rights reserved.

---

**Warning:**  
Data erasure is irreversible. Use this application only if you have proper authorization.
