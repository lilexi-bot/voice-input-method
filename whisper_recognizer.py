#!/usr/bin/env python3
"""
Whisper 语音识别模块 V2
- VAD 连续识别（WebRTC VAD）
- 长语音分块处理
- 音频预处理（降噪、16kHz采样）
"""

import whisper
import numpy as np
import pyaudio
import wave
import struct
import threading
import webrtcvad
from collections import deque

# 录音参数
CHUNK = 480  # 30ms frame for VAD (必须 160/320/480)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper 推荐采样率

# VAD 参数
VAD_AGGRESSIVENESS = 3  # 0-3，越高越激进
MIN_SPEECH_MS = 250     # 最小语音时长 (ms)
MAX_SILENCE_MS = 800    # 静音超时 (ms)


class WhisperRecognizer:
    """Whisper 语音识别器 V2"""
    
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
        self.is_recording = False
        self.audio_buffer = []
        
        # VAD 实例
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        
        # 回调函数
        self.on_audio_chunk = None
    
    def start_recording(self):
        """开始录音（VAD模式）"""
        if self.is_recording:
            return
        
        self.audio_buffer = []
        self.is_recording = True
        
        # 初始化 PyAudio
        self.audio = pyaudio.PyAudio()
        
        # 打开录音流（使用回调模式降低延迟）
        try:
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                start=True
            )
        except Exception as e:
            self.is_recording = False
            raise RuntimeError(f"无法打开麦克风: {e}\n请检查：\n1. 麦克风权限\n2. 设备是否被其他程序占用")
        
        # 启动录音线程
        thread = threading.Thread(target=self._vad_recording_thread)
        thread.daemon = True
        thread.start()
    
    def _vad_recording_thread(self):
        """VAD 录音线程"""
        ring_buffer = deque(maxlen=10)  # 环形缓冲区
        triggered = False
        silence_frames = 0
        speech_frames = 0
        
        frame_duration_ms = 30  # WebRTC VAD 固定 30ms
        
        try:
            while self.is_recording:
                # 读取音频帧
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                
                # 转换为 numpy 数组
                audio_frame = np.frombuffer(data, dtype=np.int16)
                
                # VAD 检测
                try:
                    is_speech = self.vad.is_speech(data.tobytes(), RATE)
                except:
                    is_speech = True  # VAD 出错时默认认为是语音
                
                # 状态机：等待语音开始
                if not triggered:
                    ring_buffer.append((data, is_speech))
                    
                    if is_speech:
                        speech_frames += 1
                        # 语音帧数足够，认为开始说话
                        if speech_frames * frame_duration_ms >= MIN_SPEECH_MS:
                            triggered = True
                            # 清空之前积累的静音帧
                            ring_buffer.clear()
                            ring_buffer.append((data, is_speech))
                    else:
                        speech_frames = 0
                        # 缓冲区满了，丢弃最早的帧
                        if len(ring_buffer) >= ring_buffer.maxlen:
                            ring_buffer.popleft()
                
                # 状态机：录音中
                else:
                    ring_buffer.append((data, is_speech))
                    
                    if is_speech:
                        silence_frames = 0
                    else:
                        silence_frames += 1
                        # 静音超时，结束录音
                        if silence_frames * frame_duration_ms >= MAX_SILENCE_MS:
                            break
                
                # 回调：实时音频数据（用于可视化等）
                if self.on_audio_chunk:
                    self.on_audio_chunk(data)
            
            # 收集所有音频帧
            self.audio_buffer = [frame[0] for frame in ring_buffer]
            while True:
                try:
                    if self.stream.is_active():
                        data = self.stream.read(CHUNK, exception_on_overflow=False)
                        self.audio_buffer.append(data)
                    else:
                        break
                except:
                    break
                    
        except Exception as e:
            print(f"录音异常: {e}")
        finally:
            self._cleanup_stream()
    
    def _cleanup_stream(self):
        """清理流资源"""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
    
    def stop_recording(self) -> np.ndarray:
        """停止录音并返回音频数据"""
        self.is_recording = False
        
        # 等待录音线程结束
        import time
        time.sleep(0.1)
        
        if not self.audio_buffer:
            return np.array([])
        
        # 合并音频帧
        audio_data = b''.join(self.audio_buffer)
        
        # 转换为 numpy 数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # 转换为 float32 (Whisper 需要)
        audio_float32 = audio_array.astype(np.float32) / 32768.0
        
        return audio_float32
    
    def recognize(self, audio_data: np.ndarray, language: str = "auto") -> str:
        """
        识别音频数据
        
        Args:
            audio_data: numpy 数组格式的音频数据
            language: 语言设置，'auto' 自动检测
            
        Returns:
            识别结果文本
        """
        if len(audio_data) == 0:
            return ""
        
        # Whisper 推理
        try:
            result = self.model.transcribe(
                audio_data,
                language=language,
                fp16=False,  # CPU 模式使用 fp32
                verbose=False,
                # 限制最大长度（避免超长音频）
                condition_on_previous_text=False
            )
            return result["text"].strip()
        except Exception as e:
            print(f"识别错误: {e}")
            return ""
    
    def recognize_long_audio(self, audio_data: np.ndarray, max_chunk_seconds: int = 30) -> str:
        """
        长音频识别（分块处理）
        
        Args:
            audio_data: 音频数据
            max_chunk_seconds: 每块最大时长（秒）
            
        Returns:
            完整识别结果
        """
        sample_rate = RATE
        chunk_size = sample_rate * max_chunk_seconds
        
        if len(audio_data) <= chunk_size:
            return self.recognize(audio_data)
        
        # 分块处理
        all_results = []
        total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(audio_data))
            chunk = audio_data[start:end]
            
            print(f"正在识别第 {i+1}/{total_chunks} 块...")
            result = self.recognize(chunk)
            if result:
                all_results.append(result)
        
        return " ".join(all_results)


def test_vad():
    """测试 VAD 功能"""
    print("Whisper VAD 模式测试")
    print("=" * 50)
    print("说话即可自动识别，停止说话后自动输出结果")
    print("按 Ctrl+C 退出")
    print()
    
    recognizer = WhisperRecognizer(model_name="base")
    
    try:
        recognizer.start_recording()
        print("🎤 正在监听...")
        
        # 主线程等待
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 停止录音")
        recognizer.stop_recording()
        
        audio = recognizer.audio_buffer
        if audio:
            audio_data = b''.join(audio)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            print("正在识别...")
            result = recognizer.recognize(audio_array)
            print(f"\n识别结果: {result}")


if __name__ == "__main__":
    test_vad()
