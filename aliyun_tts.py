import os
import time
import json
import subprocess
from typing import Optional
import requests
import uuid
import datetime
import hmac
import hashlib
import base64
import urllib.parse


class AliyunTTS:
    def __init__(self, access_key_id: str, access_key_secret: str, app_key: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.app_key = app_key
        self.token = None
        self.token_expire_time = None
    
    def synthesize(self, text: str, output_path: str, 
                   voice: str = "xiaoyun", 
                   speech_rate: int = 0, 
                   pitch_rate: int = 0,
                   audio_format: str = "wav",
                   sample_rate: int = 24000) -> str:
        """
        阿里云TTS语音合成
        """
        if not text:
            self._create_silent_audio(output_path, duration=1.0)
            return output_path
        
        # 优先尝试阿里云API
        try:
            success = self._synthesize_aliyun(text, output_path, voice, speech_rate, pitch_rate, audio_format, sample_rate)
            if success and os.path.exists(output_path):
                print(f"✅ 阿里云TTS成功: {os.path.basename(output_path)}")
                return output_path
        except Exception as e:
            print(f"❌ 阿里云TTS异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 失败时使用备用方案
        try:
            print("🔄 尝试使用Windows TTS备用方案...")
            self._synthesize_with_fallback(text, output_path)
        except Exception as e:
            print(f"❌ 备用TTS也失败: {e}")
            duration = max(2.0, len(text) / 10)
            self._create_silent_audio(output_path, duration)
        
        return output_path
    
    def _get_token(self) -> Optional[str]:
        """获取阿里云访问令牌 - 使用正确的API"""
        if self.token and self.token_expire_time and time.time() < self.token_expire_time - 60:
            return self.token
        
        try:
            # 正确的API端点和版本
            url = "https://nls-meta.cn-shanghai.aliyuncs.com/"
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            nonce = str(uuid.uuid4())
            
            # 构建参数
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
            
            # 生成签名
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
            
            print(f"🔐 正在获取阿里云Token...")
            
            response = requests.get(url, params=params, timeout=10)
            
            print(f"📡 Token请求状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📦 Token响应: {json.dumps(result, ensure_ascii=False)}")
                
                if 'Token' in result and 'Id' in result['Token']:
                    self.token = result['Token']['Id']
                    expire_time = result['Token'].get('ExpireTime', 0)
                    self.token_expire_time = expire_time
                    print(f"✅ 成功获取阿里云Token")
                    return self.token
                else:
                    print(f"❌ Token响应异常: {result}")
            else:
                print(f"❌ Token获取失败: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 获取Token异常: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _percent_encode(self, s):
        s = str(s)
        res = urllib.parse.quote(s.encode('utf-8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res
    
    def _synthesize_aliyun(self, text: str, output_path: str,
                           voice: str = "xiaoyun",
                           speech_rate: int = 0,
                           pitch_rate: int = 0,
                           audio_format: str = "wav",
                           sample_rate: int = 24000) -> bool:
        """使用阿里云语音合成API - 直接请求"""
        
        if not self.access_key_id or not self.access_key_secret:
            print("⚠️ 缺少阿里云Access Key，使用备用方案")
            return False
        
        try:
            # 获取Token
            token = self._get_token()
            if not token:
                print("⚠️ 无法获取Token，使用备用方案")
                return False
            
            # 阿里云TTS合成API
            url = "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'appkey': self.app_key,
                'token': token,
                'text': text,
                'voice': voice,
                'speech_rate': speech_rate,
                'pitch_rate': pitch_rate,
                'format': audio_format,
                'sample_rate': sample_rate
            }
            
            print(f"🎤 正在调用阿里云TTS (音色: {voice})...")
            print(f"📤 请求URL: {url}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            print(f"📡 TTS请求状态: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                print(f"📄 响应类型: {content_type}")
                
                if 'audio' in content_type or len(response.content) > 1000:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    file_size = os.path.getsize(output_path)
                    print(f"✅ 音频保存成功: {file_size} bytes")
                    return True
                else:
                    print(f"⚠️ 返回内容类型不是音频")
                    try:
                        error_text = response.text
                        print(f"⚠️ 错误响应: {error_text}")
                    except:
                        pass
            else:
                print(f"❌ 阿里云TTS失败: {response.status_code}")
                print(f"📄 响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 阿里云TTS异常: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def _create_silent_audio(self, output_path: str, duration: float = 1.0):
        """创建一个静音音频文件"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=22050:cl=mono',
                '-t', str(duration),
                '-c:a', 'pcm_s16le',
                '-ar', '22050',
                '-ac', '1',
                '-f', 'wav',
                output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception:
            with open(output_path, 'wb') as f:
                f.write(b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\xbb\x00\x00\x00\x77\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
    
    def _synthesize_with_fallback(self, text: str, output_path: str):
        """尝试多个替代方案生成语音"""
        if os.name == 'nt':
            try:
                self._synthesize_windows(text, output_path)
                return
            except Exception as e:
                print(f"❌ Windows TTS 失败: {e}")
        
        duration = max(2.0, len(text) / 10)
        self._create_silent_audio(output_path, duration)
    
    def _synthesize_windows(self, text: str, output_path: str):
        """在Windows上使用SAPI5 TTS"""
        try:
            import win32com.client as win32
            import pythoncom
            
            pythoncom.CoInitialize()
            
            try:
                speaker = win32.Dispatch("SAPI.SpVoice")
                
                stream = win32.Dispatch("SAPI.SpFileStream")
                stream.Open(output_path, 3, False)
                speaker.AudioOutputStream = stream
                speaker.Speak(text)
                stream.Close()
                
                if os.path.exists(output_path):
                    print("✅ Windows TTS 成功")
                    return
            finally:
                pythoncom.CoUninitialize()
        except ImportError:
            raise Exception("Windows TTS 需要 pywin32")


def synthesize_speech(text: str, output_path: str,
                     access_key_id: str = "",
                     access_key_secret: str = "",
                     app_key: str = "",
                     voice: str = "xiaoyun",
                     speech_rate: int = 0,
                     pitch_rate: int = 0,
                     audio_format: str = "wav",
                     sample_rate: int = 24000) -> str:
    """
    便捷函数用于语音合成
    """
    tts = AliyunTTS(access_key_id, access_key_secret, app_key)
    return tts.synthesize(text, output_path, voice, speech_rate, pitch_rate, audio_format, sample_rate)


def get_audio_duration(audio_path: str) -> float:
    """
    获取音频文件时长（秒）
    """
    if not os.path.exists(audio_path):
        return 0.0
    
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception:
        return 3.0
