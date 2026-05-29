import os
import time
import json
import base64
import hashlib
import hmac
import urllib.parse
import uuid
import datetime
import requests
from typing import Optional, Dict, Any


class AliyunASR:
    """阿里云语音识别服务"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, app_key: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.app_key = app_key
        self.token = None
        self.token_expire_time = None
    
    def _get_token(self) -> Optional[str]:
        """获取阿里云访问令牌"""
        if self.token and self.token_expire_time and time.time() < self.token_expire_time - 60:
            return self.token
        
        try:
            url = "https://nls-meta.cn-shanghai.aliyuncs.com/"
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            nonce = str(uuid.uuid4())
            
            params = {
                'Format': 'JSON',
                'Version': '2019-02-28',
                'AccessKeyId': self.access_key_id,
                'SignatureMethod': 'HMAC-SHA1',
                'Timestamp': timestamp,
                'SignatureVersion': '1.0',
                'SignatureNonce': nonce,
                'Action': 'CreateToken'
            }
            
            sorted_params = sorted(params.items())
            query_string = '&'.join([
                self._percent_encode(k) + '=' + self._percent_encode(v)
                for k, v in sorted_params
            ])
            
            string_to_sign = 'GET&%2F&' + self._percent_encode(query_string)
            key = self.access_key_secret + '&'
            h = hmac.new(key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
            signature = base64.b64encode(h.digest()).strip().decode('utf-8')
            
            params['Signature'] = signature
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'Token' in result and 'Id' in result['Token']:
                    self.token = result['Token']['Id']
                    expire_time = result['Token'].get('ExpireTime', 0)
                    self.token_expire_time = expire_time
                    return self.token
        except Exception as e:
            print(f"获取Token异常: {e}")
        
        return None
    
    def _percent_encode(self, s):
        s = str(s)
        res = urllib.parse.quote(s.encode('utf-8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res
    
    def recognize_file(self, audio_path: str) -> Optional[str]:
        """识别音频文件（使用文件识别接口）"""
        if not os.path.exists(audio_path):
            print(f"音频文件不存在: {audio_path}")
            return None
        
        try:
            token = self._get_token()
            if not token:
                print("无法获取ASR Token")
                return None
            
            # 使用文件识别API而不是流式API
            url = "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr"
            
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            sample_rate = 16000
            format_str = os.path.splitext(audio_path)[1].lower().replace('.', '')
            if format_str == 'mp3':
                format_str = 'mp3'
            elif format_str == 'wav':
                format_str = 'wav'
            else:
                format_str = 'wav'
            
            # 正确的请求格式 - 直接发送JSON，音频base64编码
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                'appkey': self.app_key,
                'token': token,
                'format': format_str,
                'sample_rate': sample_rate,
                'enable_intermediate_result': False,
                'enable_punctuation_prediction': True,
                'enable_inverse_text_normalization': True,
                'audio': audio_base64
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            print(f"正在调用阿里云ASR识别: {os.path.basename(audio_path)}")
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusText') == 'SUCCESS':
                    text = result.get('Result', '')
                    print(f"✅ ASR识别成功，文本长度: {len(text)}")
                    return text
                else:
                    print(f"ASR识别失败: {result.get('StatusText')}")
                    print(f"错误信息: {result.get('ErrorMessage', '无')}")
            else:
                print(f"ASR请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"ASR识别异常: {e}")
            import traceback
            traceback.print_exc()
        
        return None


def recognize_speech(audio_path: str,
                    access_key_id: str = "",
                    access_key_secret: str = "",
                    app_key: str = "") -> Optional[str]:
    """便捷函数进行语音识别"""
    asr = AliyunASR(access_key_id, access_key_secret, app_key)
    return asr.recognize_file(audio_path)
