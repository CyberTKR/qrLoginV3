from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport
from thrift.Thrift import TMessageType, TType
from .ttypes import *
import json
from .qrTools import parse_qr_login_response_to_json

class ThriftProtocolHandler:
    def create_session(self):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("createSession", TMessageType.CALL, 1)
        proto.writeStructBegin("createSession_args")
        
        request = CreateSessionRequest()
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        request.write(proto)
        proto.writeFieldEnd()
        
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def parse_session_response(self, response_content):
        transport = TTransport.TMemoryBuffer(response_content)
        proto = TCompactProtocol.TCompactProtocol(transport)
        
        try:
            name, msg_type, seqid = proto.readMessageBegin()
            
            proto.readStructBegin()
            session_id = None
            
            while True:
                field_name, field_type, field_id = proto.readFieldBegin()
                if field_type == TType.STOP:
                    break
                    
                if field_id == 0 and field_type == TType.STRUCT:
                    inner_struct_name = proto.readStructBegin()
                    
                    while True:
                        inner_field_name, inner_field_type, inner_field_id = proto.readFieldBegin()
                        if inner_field_type == TType.STOP:
                            break
                            
                        if inner_field_type == TType.STRING:
                            session_id = proto.readString()
                            return session_id
                        else:
                            proto.skip(inner_field_type)
                            
                        proto.readFieldEnd()
                        
                    proto.readStructEnd()
                else:
                    proto.skip(field_type)
                    
                proto.readFieldEnd()
                
            proto.readStructEnd()
            proto.readMessageEnd()
            
        except Exception as e:
            print(f"Parse error: {str(e)}")
            import traceback
            traceback.print_exc()
        return None

    def create_qr_code(self, session_id):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("createQrCodeForSecure", TMessageType.CALL, 1)
        proto.writeStructBegin("createQrCodeForSecure_args")
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        
        proto.writeStructBegin("CreateQrCodeRequest")
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def parse_qr_code_response(self, response_content):
        transport = TTransport.TMemoryBuffer(response_content)
        proto = TCompactProtocol.TCompactProtocol(transport)
        
        try:
            name, msg_type, seqid = proto.readMessageBegin()
            
            proto.readStructBegin()
            result = CreateQrCodeForSecureResponse()
            
            while True:
                field_name, field_type, field_id = proto.readFieldBegin()
                if field_type == TType.STOP:
                    break
                    
                if field_id == 0 and field_type == TType.STRUCT:
                    inner_struct_name = proto.readStructBegin()
                    
                    while True:
                        inner_field_name, inner_field_type, inner_field_id = proto.readFieldBegin()
                        if inner_field_type == TType.STOP:
                            break
                            
                        if inner_field_type == TType.STRING:
                            if inner_field_id == 1:
                                result.callbackUrl = proto.readString()
                            elif inner_field_id == 4:
                                result.nonce = proto.readString()
                        elif inner_field_type == TType.I32:
                            if inner_field_id == 2:
                                result.longPollingMaxCount = proto.readI32()
                            elif inner_field_id == 3:
                                result.longPollingIntervalSec = proto.readI32()
                        else:
                            proto.skip(inner_field_type)
                            
                        proto.readFieldEnd()
                        
                    proto.readStructEnd()
                else:
                    proto.skip(field_type)
                    
                proto.readFieldEnd()
                
            proto.readStructEnd()
            proto.readMessageEnd()
            
            return result
            
        except Exception as e:
            print(f"Parse error: {str(e)}")
            import traceback
            traceback.print_exc()
        return None

    def check_qr_code_verified(self, session_id):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("checkQrCodeVerified", TMessageType.CALL, 1)
        proto.writeStructBegin("checkQrCodeVerified_args")
        
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        proto.writeStructBegin("CheckQrCodeVerifiedRequest")
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def create_pin_code(self, session_id):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("createPinCode", TMessageType.CALL, 3)
        proto.writeStructBegin("createPinCode_args")
        
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        proto.writeStructBegin("CreatePinCodeRequest")
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def parse_pin_code_response(self, response_content):
        transport = TTransport.TMemoryBuffer(response_content)
        proto = TCompactProtocol.TCompactProtocol(transport)
        
        try:
            name, msg_type, seqid = proto.readMessageBegin()
            
            if msg_type == TMessageType.EXCEPTION:
                x = TApplicationException()
                x.read(proto)
                proto.readMessageEnd()
                print(f"Thrift Exception: {x.message}")
                return None
            
            proto.readStructBegin()
            result = CreatePinCodeResponse()
            
            while True:
                field_name, field_type, field_id = proto.readFieldBegin()
                if field_type == TType.STOP:
                    break
                
                if field_id == 0:  # Response struct
                    result.read(proto)
                else:
                    proto.skip(field_type)
                
                proto.readFieldEnd()
            
            proto.readStructEnd()
            proto.readMessageEnd()
            
            return result.pinCode
            
        except Exception as e:
            print(f"PIN code parse error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def check_pin_code_verified(self, session_id):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("checkPinCodeVerified", TMessageType.CALL, 3)
        proto.writeStructBegin("checkPinCodeVerified_args")
        
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        proto.writeStructBegin("CheckPinCodeVerifiedRequest")
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def verify_qr_code_login(self, session_id, nonce, system_name, model_name="MAC"):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("qrCodeLoginV2ForSecure", TMessageType.CALL, 1)
        proto.writeStructBegin("qrCodeLoginV2ForSecure_args")
        
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        proto.writeStructBegin("QrCodeLoginV2ForSecureRequest")
        
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        
        proto.writeFieldBegin("systemName", TType.STRING, 2)
        proto.writeString(system_name)
        proto.writeFieldEnd()
        
        proto.writeFieldBegin("modelName", TType.STRING, 3)
        proto.writeString(model_name)
        proto.writeFieldEnd()
        
        proto.writeFieldBegin("autoLoginIsRequired", TType.BOOL, 4)
        proto.writeBool(True)
        proto.writeFieldEnd()
        
        proto.writeFieldBegin("nonce", TType.STRING, 5)
        proto.writeString(nonce)
        proto.writeFieldEnd()
        
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def parse_qr_code_login_response(self, response_content):
        transport = TTransport.TMemoryBuffer(response_content)
        proto = TCompactProtocol.TCompactProtocol(transport)
        
        try:
            name, msg_type, seqid = proto.readMessageBegin()
            
            proto.readStructBegin()
            
            while True:
                fname, ftype, fid = proto.readFieldBegin()
                if ftype == TType.STOP:
                    break
                    
                if fid == 0:
                    if ftype == TType.STRUCT:
                        result = QrCodeLoginV2Response()
                        result.read(proto)
                        certificate = result.certificate
                        try:
                            parsed_data = json.loads(parse_qr_login_response_to_json(response_content))
                            if certificate:
                                parsed_data['certificate'] = certificate
                            return True, json.dumps(parsed_data, indent=2)
                        except Exception as e:
                            print(f"Parse Error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            return False
                else:
                    proto.skip(ftype)
                    
                proto.readFieldEnd()
            
            proto.readStructEnd()
            proto.readMessageEnd()
            
            return False
            
        except Exception as e:
            print(f"Thrift decode error: {str(e)}")
            import traceback
            traceback.print_exc()
        return False

    def verify_certificate(self, session_id, certificate=None):
        buf = TTransport.TMemoryBuffer()
        proto = TCompactProtocol.TCompactProtocol(buf)
        
        proto.writeMessageBegin("verifyCertificate", TMessageType.CALL, 1)
        proto.writeStructBegin("verifyCertificate_args")
        
        proto.writeFieldBegin("request", TType.STRUCT, 1)
        proto.writeStructBegin("VerifyCertificateRequest")
        
        proto.writeFieldBegin("authSessionId", TType.STRING, 1)
        proto.writeString(session_id)
        proto.writeFieldEnd()
        
        if certificate:
            proto.writeFieldBegin("certificate", TType.STRING, 2)
            proto.writeString(certificate)
            proto.writeFieldEnd()
        
        proto.writeFieldStop()
        proto.writeStructEnd()
        
        proto.writeFieldEnd()
        proto.writeFieldStop()
        proto.writeStructEnd()
        proto.writeMessageEnd()
        
        return buf.getvalue()

    def parse_certificate_response(self, response_content):
        transport = TTransport.TMemoryBuffer(response_content)
        proto = TCompactProtocol.TCompactProtocol(transport)
        
        try:
            name, msg_type, seqid = proto.readMessageBegin()
            
            if msg_type == TMessageType.EXCEPTION:
                x = TApplicationException()
                x.read(proto)
                proto.readMessageEnd()
                print(f"Thrift Exception: {x.message}")
                return None
            
            proto.readStructBegin()
            result = VerifyCertificateResponse()
            
            while True:
                field_name, field_type, field_id = proto.readFieldBegin()
                if field_type == TType.STOP:
                    break
                
                if field_id == 0:  # Response struct
                    result.read(proto)
                else:
                    proto.skip(field_type)
                
                proto.readFieldEnd()
            
            proto.readStructEnd()
            proto.readMessageEnd()
            
            return result
            
        except Exception as e:
            print(f"Certificate response parse error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 