import os
from typing import Optional


class ASRService:
    """语音识别服务 - 支持阿里云ASR和本地Whisper"""

    def __init__(self, use_local: bool = False):
        self.use_local = use_local
        self.whisper_model = None

    def _load_whisper(self):
        """加载Whisper模型"""
        try:
            import whisper
            if self.whisper_model is None:
                print("📥 正在加载Whisper模型 (base)...")
                self.whisper_model = whisper.load_model("base")
            return True
        except ImportError:
            print("❌ 未安装whisper库，请运行: pip install openai-whisper")
            return False
        except Exception as e:
            print(f"❌ 加载Whisper模型失败: {e}")
            return False

    def recognize_local(self, audio_path: str) -> Optional[str]:
        """使用本地Whisper进行语音识别"""
        if not os.path.exists(audio_path):
            print(f"❌ 音频文件不存在: {audio_path}")
            return None

        if not self._load_whisper():
            return None

        try:
            print(f"🎯 正在使用本地Whisper识别: {os.path.basename(audio_path)}")
            result = self.whisper_model.transcribe(audio_path, language="zh")
            text = result.get("text", "").strip()
            print(f"✅ 本地识别成功，文本长度: {len(text)}")
            return text
        except Exception as e:
            print(f"❌ 本地识别失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def recognize_aliyun(self, audio_path: str, access_key_id: str = "", 
                        access_key_secret: str = "", app_key: str = "") -> Optional[str]:
        """使用阿里云ASR进行语音识别"""
        # 导入aliyun_asr模块
        try:
            from aliyun_asr import AliyunASR
        except ImportError:
            print("❌ 无法导入aliyun_asr模块")
            return None

        if not os.path.exists(audio_path):
            print(f"❌ 音频文件不存在: {audio_path}")
            return None

        try:
            asr = AliyunASR(access_key_id, access_key_secret, app_key)
            return asr.recognize_file(audio_path)
        except Exception as e:
            print(f"❌ 阿里云识别失败: {e}")
            return None

    def recognize(self, audio_path: str, access_key_id: str = "", 
                 access_key_secret: str = "", app_key: str = "") -> Optional[str]:
        """统一的识别接口"""
        if self.use_local:
            return self.recognize_local(audio_path)
        else:
            return self.recognize_aliyun(audio_path, access_key_id, access_key_secret, app_key)


def recognize_speech(audio_path: str, use_local: bool = False,
                    access_key_id: str = "",
                    access_key_secret: str = "",
                    app_key: str = "") -> Optional[str]:
    """便捷识别函数"""
    service = ASRService(use_local=use_local)
    return service.recognize(audio_path, access_key_id, access_key_secret, app_key)
