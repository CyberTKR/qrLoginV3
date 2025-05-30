from dataclasses import dataclass
from typing import Tuple, Optional, Union
from urllib.parse import quote
from base64 import b64encode
import axolotl_curve25519 as curve
import qrcode
import qrcode.image.pure
import os
from LineQrThrift.LineThriftClient import LineThriftClient
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

@dataclass
class QrSecret:
    private_key: bytes
    public_key: str
    secret_url: str
    version: int = 1

class QrCodeGenerator:
    def __init__(self, box_size: int = 1, border: int = 1):
        self.box_size = box_size
        self.border = border

    def generate_console_qr(self, url: str) -> str:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr.print_ascii(invert=True)
        return ""

class SecurityManager:
    @staticmethod
    def generate_secret(base64: bool = False) -> Union[Tuple[bytes, str], Tuple[bytes, str]]:
        private_key = curve.generatePrivateKey(os.urandom(32))
        public_key = curve.generatePublicKey(private_key)
        secret = quote(b64encode(public_key).decode())
        
        if base64:
            return private_key, b64encode(public_key).decode()
        return private_key, f"?secret={secret}&e2eeVersion=1"

class LineQrLogin:
    def __init__(self):
        self.client = LineThriftClient()
        self.qr_generator = QrCodeGenerator()
        self.security_manager = SecurityManager()

    def start_login_process(self) -> None:
        if not self._initialize_session():
            return

        qr_result = self._create_qr_code()
        if not qr_result:
            return

        self._handle_qr_verification(qr_result)

    def _initialize_session(self) -> bool:
        session_id = self.client.create_session()
        if not session_id:
            print(f"{Fore.RED}Failed to create session!{Style.RESET_ALL}")
            return False
        print(f"{Fore.CYAN}Session ID: {Fore.GREEN}{session_id}{Style.RESET_ALL}")
        return True

    def _create_qr_code(self) -> Optional[object]:
        qr_result = self.client.create_qr_code()
        if not qr_result:
            print(f"{Fore.RED}Failed to create QR code!{Style.RESET_ALL}")
            return None

        secret, secret_url = self.security_manager.generate_secret()
        url = qr_result.callbackUrl + secret_url
        print(f"{Fore.CYAN}Scan this QR code:{Style.RESET_ALL}")
        print(self.qr_generator.generate_console_qr(url))
        return qr_result
    def get_certificate(self):
        """
        Read QR code verification certificate from current directory.
        Certificate is stored as cert.pem
        
        Returns:
            str: Certificate content if file exists
            None: If file not found
        """
        try:
            cert_file = os.path.join(os.getcwd(), 'cert.pem')
            
            if os.path.exists(cert_file):
                with open(cert_file, 'r') as f:
                    return f.read()
                    
            return None
            
        except Exception as e:
            print(f"{Fore.RED}Certificate read error: {str(e)}{Style.RESET_ALL}")
            return None
    def _handle_qr_verification(self, qr_result: object) -> None:
        print(f"\n{Fore.CYAN}Please scan and verify the QR code...{Style.RESET_ALL}")
        
        if self.client.check_qr_code_verified():
            print(f"{Fore.GREEN}QR code verification successful!{Style.RESET_ALL}")
            
            if self.client.verify_certificate(self.get_certificate()):
                print(f"{Fore.GREEN}Certificate verification successful!{Style.RESET_ALL}")
                self._complete_login(qr_result)
            else:
                print(f"{Fore.YELLOW}Certificate verification failed, proceeding with PIN code...{Style.RESET_ALL}")
                pin_code = self.client.create_pin_code()
                print(f"{Fore.CYAN}PIN Code: {Fore.YELLOW}{pin_code}{Style.RESET_ALL}")
                
                if self.client.check_pin_code_verified():
                    print(f"{Fore.GREEN}PIN code verification successful!{Style.RESET_ALL}")
                    self._complete_login(qr_result)
                else:
                    print(f"{Fore.RED}PIN code verification failed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}QR code verification failed!{Style.RESET_ALL}")

    def _complete_login(self, qr_result: object) -> None:
        if not self.client.session_id:
            print(f"{Fore.RED}Session ID not found!{Style.RESET_ALL}")
            return
            
        login_result = self.client.verify_qr_code_login(qr_result.nonce)
        if login_result:
            print(f"{Fore.GREEN}QR code login successful!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Login information: {Fore.GREEN}{login_result}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}QR code login failed!{Style.RESET_ALL}")


def main():
    login_manager = LineQrLogin()
    login_manager.start_login_process()

if __name__ == "__main__":
    main()