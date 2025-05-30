# LINE QR Login

This project implements a QR code-based login system for LINE using their Thrift API. It provides a simple way to authenticate with LINE using QR codes and PIN verification.

## Features

- QR Code Generation and Display in Console
- Certificate-based Authentication
- PIN Code Verification
- Secure E2EE Implementation
- Colorized Console Output

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

```python
from qrloginv3.qr import LineQrLogin

# Initialize the login manager
login_manager = LineQrLogin()

# Start the login process
login_manager.start_login_process()
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/qrLoginV3.git
cd qrLoginV3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How it works

1. Creates a session with LINE servers
2. Generates a QR code for scanning
3. Waits for QR code verification
4. Handles certificate verification
5. Falls back to PIN verification if needed
6. Completes login process

## License

MIT License 