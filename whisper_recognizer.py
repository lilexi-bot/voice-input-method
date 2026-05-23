#!/usr/bin/env python3
"""
Whisper 语音识别模块
基于 OpenAI Whisper 的本地语音识别
"""

import whisper
import numpy as np
import pyaudio
import wave
import tempfile
import os

# 录音参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper 推荐采样率


class WhisperRecognizer:
    """Whisper 语音识别器"""
    
    def __init__(self, model_name: str = "base"):
        """
        初始化识别器
        
        Args:
            model_name: Whisper 模型名称 (tiny/base/small/medium/large)
        """
        self.model_name = model_name
        print(f"正在加载 Whisper {model_name} 模型...")
        self.model = whisper.load_model(model_name)
        print("模型加载完成")
        
        # PyAudio 实例
        self.audio = None
        self.stream = None
        
        # 录音状态
        self.frames = []
        self.is_recording = False
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
        self.frames = []
        self.is_recording = True
        
        # 初始化 PyAudio
        self.audio = pyaudio.PyAudio()
        
        # 打开录音流
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            start=True
        )
        
        # 录音线程
        import threading
        thread = threading.Thread(target=self._record_thread)
        thread.daemon = True
        thread.start()
    
    def _record_thread(self):
        """录音线程：持续采集音频"""
        try:
            while self.is_recording:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            print(f"录音异常: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
    
    def stop_recording(self) -> np.ndarray:
        """停止录音并返回音频数据"""
        self.is_recording = False
        
        if not self.frames:
            return np.array([])
        
        # 合并音频帧
        audio_data = b''.join(self.frames)
        
        # 转换为 numpy 数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # 转换为 float32 (Whisper 需要)
        audio_float32 = audio_array.astype(np.float32) / 32768.0
        
        return audio_float32
    
    def recognize(self, audio_data: np.ndarray) -> str:
        """
        识别音频数据
        
        Args:
            audio_data: numpy 数组格式的音频数据
            
        Returns:
            识别结果文本
        """
        if len(audio_data) == 0:
            return ""
        
        # Whisper 推理
        result = self.model.transcribe(
            audio_data,
            language='auto',  # 自动检测语言
            fp16=False,       # CPU 模式使用 fp32
            verbose=False
        )
        
        return result["text"].strip()
    
    def recognize_from_file(self, audio_path: str) -> str:
        """
        从音频文件识别
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            识别结果文本
        """
        # 加载音频
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_truncate(audio, whisper.audio.SAMPLE_RATE * 30)  # 最大30秒
        
        # 识别
        result = self.model.transcribe(
            audio,
            language='auto',
            fp16=False,
            verbose=False
        )
        
        return result["text"].strip()


def main():
    """测试函数"""
    print("Whisper 语音识别测试")
    print("=" * 50)
    
    recognizer = WhisperRecognizer(model_name="base")
    
    print("\n按 Enter 开始录音...")
    input()
    
    print("正在录音（按 Enter 停止）...")
    recognizer.start_recording()
    input()
    
    print("正在识别...")
    audio_data = recognizer.stop_recording()
    
    if len(audio_data) > 0:
        result = recognizer.recognize(audio_data)
        print(f"\n识别结果: {result}")
    else:
        print("未检测到音频")


if __name__ == "__main__":
    main()
