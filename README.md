# LINE QR Login 🔐

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![LINE](https://img.shields.io/badge/LINE-API-00C300.svg)](https://developers.line.biz/)
[![GitHub stars](https://img.shields.io/github/stars/CyberTKR/qrLoginV3?style=social)](https://github.com/CyberTKR/qrLoginV3/stargazers)

<img src="https://github.com/CyberTKR/CyberTKR/raw/main/code.gif" width="500" height="300">

</div>

This project implements a QR code-based login system for LINE using their Thrift API. It provides a simple way to authenticate with LINE using QR codes and PIN verification.

## ✨ Features

- 📱 QR Code Generation and Display in Console
- 🔒 Certificate-based Authentication
- 🔑 PIN Code Verification
- 🛡️ Secure E2EE Implementation
- 🎨 Colorized Console Output

## 📋 Requirements

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```python
from qrloginv3.qr import LineQrLogin

# Initialize the login manager
login_manager = LineQrLogin()

# Start the login process
login_manager.start_login_process()
```

## 💻 Installation

1. Clone the repository:
```bash
git clone https://github.com/CyberTKR/qrLoginV3.git
cd qrLoginV3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🔄 How it works

1. Creates a session with LINE servers
2. Generates a QR code for scanning
3. Waits for QR code verification
4. Handles certificate verification
5. Falls back to PIN verification if needed
6. Completes login process

## 📞 Contact & Social Media

<div align="center">

### Connect with me:
[![LINE](https://img.shields.io/badge/LINE-00C300?style=for-the-badge&logo=line&logoColor=white)](https://line.me/ti/p/ZLLfrcvarH)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@cybertkr?si=gerNF_w9S_ZW5S1a)

</div>

## 📄 License

MIT License 