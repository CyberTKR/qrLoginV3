import re
import json
import base64
from datetime import datetime
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from io import StringIO
import os

@dataclass
class TokenInfo:
    aid: str
    iat: int
    exp: int

@dataclass
class QrLoginMetadata:
    hash_key_chain: Optional[str] = None
    key_id: Optional[str] = None
    public_key: Optional[str] = None
    e2ee_version: Optional[str] = None

@dataclass
class QrLoginResponse:
    mid: str
    auth_token_v3: str
    issued_at: str
    expired_at: str
    refresh_v3_token: Optional[str] = None
    certificate: str = ""
    metadata: QrLoginMetadata = None
    token_info: Optional[Dict[str, Any]] = None

class Base64Utils:
    @staticmethod
    def is_base64(data: Union[str, bytes]) -> bool:
        try:
            if isinstance(data, str):
                data_bytes = data.encode('ascii')
            else:
                data_bytes = data
            return base64.b64encode(base64.b64decode(data_bytes)) == data_bytes
        except Exception:
            return False

class JwtUtils:
    @staticmethod
    def decode_payload(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
                
            payload = parts[1]
            padding = '=' * (-len(payload) % 4)
            decoded_bytes = base64.urlsafe_b64decode(payload + padding)
            return json.loads(decoded_bytes.decode('utf-8'))
        except Exception:
            return None

class DateTimeUtils:
    @staticmethod
    def timestamp_to_str(timestamp: Optional[int]) -> Optional[str]:
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp).isoformat()

class QrLoginParser:
    def __init__(self):
        self.base64_utils = Base64Utils()
        self.jwt_utils = JwtUtils()
        self.datetime_utils = DateTimeUtils()

    def parse_response(self, response: bytes) -> str:
        decoded_fields = self._extract_fields(response)
        data = self._process_fields(decoded_fields, response)
        result = self._create_response_object(data)
        return json.dumps(result, indent=2)

    def _extract_fields(self, byte_data: bytes) -> list:
        pattern = rb'([ -~]{4,})'
        matches = re.findall(pattern, byte_data)
        return [m.decode(errors='ignore') for m in matches]

    def _process_fields(self, fields: list, byte_data: bytes) -> Dict[str, Any]:
        data = {}
        
        for field in fields:
            self._process_field(field, data)
        
        self._extract_special_fields(byte_data, data)
        
        if data.get('token'):
            decoded = self.jwt_utils.decode_payload(data['token'])
            if decoded:
                data['token_info'] = decoded
        
        return data

    def _process_field(self, field: str, data: Dict[str, Any]) -> None:
        if 'qrCodeLoginV2ForSecure' in field:
            data['method'] = field
        elif re.fullmatch(r'[a-f0-9]{64}', field):
            data['id'] = field
        elif field.startswith('eyJ') and len(field) > 100:
            if 'token' not in data:
                data['token'] = field
            else:
                data['rt'] = field
        elif re.match(r'^[A-Za-z0-9+/=]{40,}$', field):
            if 'publicKey' not in data:
                data['publicKey'] = field
            elif 'certificate' not in data:
                data['certificate'] = field
        elif self.base64_utils.is_base64(field) and len(field) > 100:
            data['encryptedKeyChain'] = field

    def _extract_special_fields(self, byte_data: bytes, data: Dict[str, Any]) -> None:
        patterns = {
            'publicKey': (rb'publicKey,([A-Za-z0-9+/=]+)', 1),
            'e2eeVersion': (rb'e2eeVersion\x01(\d)', 1),
            'hashKeyChain': (rb'hashKeyChain\x18([A-Za-z0-9+/=]+)', 1),
            'keyId': (rb'keyId\x07([0-9]+)', 1),
            'encryptedKeyChain': (rb'encryptedKeyChain\xd8\x02R(.+?)\x0chashKeyChain', 1)
        }

        for key, (pattern, group) in patterns.items():
            match = re.search(pattern, byte_data, re.DOTALL if key == 'encryptedKeyChain' else 0)
            if match:
                value = match.group(group)
                if key == 'encryptedKeyChain':
                    value = value.rstrip(b"\x00").decode(errors="ignore")
                else:
                    value = value.decode()
                data[key] = value

    def _create_response_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        token_info = data.get('token_info', {})
        
        metadata = QrLoginMetadata(
            hash_key_chain=data.get('hashKeyChain'),
            key_id=data.get('keyId'),
            public_key=data.get('publicKey'),
            e2ee_version=data.get('e2eeVersion')
        )

        return {
            'mid': token_info.get('aid', ''),
            'authTokenV3': data.get('token', ''),
            'issuedAt': self.datetime_utils.timestamp_to_str(token_info.get('iat')),
            'expiredAt': self.datetime_utils.timestamp_to_str(token_info.get('exp')),
            'RefreshV3Token': data.get('rt'),
            'certificate': data.get('certificate', ''),
            'metadata': metadata.__dict__,
            'tokenInfo': token_info
        }

def parse_qr_login_response_to_json(response: bytes) -> str:
    parser = QrLoginParser()
    return parser.parse_response(response)

