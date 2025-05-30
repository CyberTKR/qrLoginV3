import httpx
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport
from thrift.Thrift import TMessageType, TType, TApplicationException
from .api.ttypes import *
import random, string
import json
from .api.SecondaryQrCodeLoginService import ThriftProtocolHandler
from colorama import Fore, Style


class LineThriftClient:
    def __init__(self):
        self.session_id = None
        self.base_url = "https://ga2.line.naver.jp/acct/lgn/sq/v1"
        self.long_polling_url = "https://gw.line.naver.jp/acct/lp/lgn/sq/v1"
        self.client = httpx.Client(http2=True)
        self.protocol = ThriftProtocolHandler()

    def _create_headers(self, extra_headers=None, with_access: bool = False):
        headers = {
            "User-Agent": "Line/8.7.0",
            "X-Line-Application": "DESKTOPMAC\t8.7.0\tMAC\t10.15.7",
            "Content-Type": "application/x-thrift; protocol=TCOMPACT",
            "x-lal": "tr_TR",
            "x-lhm": "POST",
            "x-client-ip": self._generate_random_ip(),
            "x-forwarded-for": self._generate_random_ip()
        }
        if with_access and self.session_id:
            headers["X-Line-Access"] = self.session_id
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def _generate_random_ip():
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    @staticmethod
    def _generate_random_system():
        prefix = random.choice(["DESKTOP", "MOBILE", "CHROME", "LINUX", "WIN", "MAC", "TABLET", "TV"])
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(4,8)))
        return f"{prefix}_{suffix}"

    def create_session(self):
        request_content = self.protocol.create_session()
        response = self.client.post(self.base_url, headers=self._create_headers(), content=request_content)
        if response.status_code == 200:
            self.session_id = self.protocol.parse_session_response(response.content)
            return self.session_id
        return None

    def create_qr_code(self):
        if not self.session_id:
            return None
        request_content = self.protocol.create_qr_code(self.session_id)
        response = self.client.post(self.base_url, headers=self._create_headers(), content=request_content)
        if response.status_code == 200:
            return self.protocol.parse_qr_code_response(response.content)
        return None

    def check_qr_code_verified(self):
        if not self.session_id:
            return None
        request_content = self.protocol.check_qr_code_verified(self.session_id)
        headers = self._create_headers({"x-lst": "150000"}, with_access=True)
        try:
            response = self.client.post(self.long_polling_url, headers=headers, content=request_content, timeout=180.0)
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False

    def create_pin_code(self):
        if not self.session_id:
            print(f"{Fore.RED}Session ID not found!{Style.RESET_ALL}")
            return None
        request_content = self.protocol.create_pin_code(self.session_id)
        try:
            response = self.client.post(self.base_url, headers=self._create_headers(), content=request_content)
            if response.status_code == 200:
                pin_code = self.protocol.parse_pin_code_response(response.content)
                if pin_code:
                    return pin_code
                print(f"{Fore.RED}Failed to parse PIN code response!{Style.RESET_ALL}")
                return None
            print(f"{Fore.RED}Error creating PIN code: {response.status_code}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}Error creating PIN code: {str(e)}{Style.RESET_ALL}")
            return None

    def check_pin_code_verified(self):
        if not self.session_id:
            return None
        request_content = self.protocol.check_pin_code_verified(self.session_id)
        headers = self._create_headers({"x-lst": "150000"}, with_access=True)
        try:
            response = self.client.post(self.long_polling_url, headers=headers, content=request_content, timeout=180.0)
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False

    def verify_qr_code_login(self, nonce):
        if not self.session_id:
            print(f"{Fore.RED}Session ID not found!{Style.RESET_ALL}")
            return None
        request_content = self.protocol.verify_qr_code_login(
            self.session_id,
            nonce,
            self._generate_random_system()
        )
        try:
            response = self.client.post(self.base_url, headers=self._create_headers(), content=request_content)
            if response.status_code == 200:
                result = self.protocol.parse_qr_code_login_response(response.content)
                if isinstance(result, tuple) and len(result) == 2:
                    success, login_data = result
                    if success and login_data:
                        try:
                            login_json = json.loads(login_data)
                            if 'certificate' in login_json and login_json['certificate']:
                                print(f"{Fore.GREEN}Certificate found: {login_json['certificate']}{Style.RESET_ALL}")
                            return login_data
                        except json.JSONDecodeError:
                            print(f"{Fore.RED}Login data is not in JSON format{Style.RESET_ALL}")
                            return False
                return False
            return False
        except Exception as e:
            print(f"{Fore.RED}QR login error: {str(e)}{Style.RESET_ALL}")
            return False

    def verify_certificate(self, certificate=None):
        print(f"{Fore.CYAN}Starting certificate verification...{Style.RESET_ALL}")
        if not self.session_id:
            print(f"{Fore.RED}Session ID not found!{Style.RESET_ALL}")
            return False
            
        request_content = self.protocol.verify_certificate(self.session_id, certificate)
        response = self.client.post(self.base_url, headers=self._create_headers(), content=request_content)
        
        # Check for binary error message
        if b'verifyCertificate' in response.content:
            print(f"{Fore.YELLOW}Certificate verification failed!{Style.RESET_ALL}")
            return False
            
        if response.status_code == 200:
            try:
                result = self.protocol.parse_certificate_response(response.content)
                if result is not None:
                    return True
            except Exception as e:
                print(f"{Fore.RED}Certificate parse error: {str(e)}{Style.RESET_ALL}")
                return False
                
        return False