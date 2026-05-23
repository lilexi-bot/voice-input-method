#!/usr/bin/env python3
"""
Voice Input Method - 主程序入口 V3
- VAD 连续识别
- 云端/本地模式切换
- Demo 演示模式
"""

import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip
import sys
import os

from ui import VoiceInputUI
from whisper_recognizer import WhisperRecognizer
from text_processor import TextProcessor

# 尝试导入七牛云ASR（可选）
try:
    from qiniu_asr import QiniuASR
    QINIU_ASR_AVAILABLE = True
except ImportError:
    QINIU_ASR_AVAILABLE = False


class VoiceInputApp:
    """语音输入法主应用 V3"""
    
    def __init__(self):
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("Voice Input Method - 语音输入法 V3")
        self.root.geometry("620x480")
        self.root.resizable(True, True)
        
        # 模式配置
        self.use_cloud_api = False  # 默认本地模式
        
        # 初始化模块
        try:
            self.recognizer = WhisperRecognizer()
            self.processor = TextProcessor()
            if QINIU_ASR_AVAILABLE:
                self.qiniu_asr = QiniuASR()
            else:
                self.qiniu_asr = None
        except Exception as e:
            self._show_fatal_error(f"初始化失败: {e}")
            raise
        
        # 初始化UI
        self.ui = VoiceInputUI(
            root=self.root,
            on_record_start=self.start_recording,
            on_record_stop=self.stop_recording,
            on_copy=self.copy_text,
            on_mode_switch=self.toggle_mode,
            use_cloud_api=self.use_cloud_api,
            cloud_available=QINIU_ASR_AVAILABLE
        )
        
        # 状态变量
        self.is_recording = False
        self.current_text = ""
        self.is_initialized = True
        
        # 绑定快捷键
        self._bind_shortcuts()
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 更新模式显示
        self._update_mode_display()
    
    def _update_mode_display(self):
        """更新模式显示"""
        mode = "云端高精度" if self.use_cloud_api else "本地Whisper"
        status = f"就绪 | 当前模式: {mode}"
        self.ui.set_status(status)
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        # 空格键
        self.root.bind('<space>', self._on_space_press)
        self.root.bind('<KeyRelease-space>', self._on_space_release)
        
        # Ctrl+Enter 强制识别
        self.root.bind('<Control-Return>', lambda e: self.stop_recording())
        
        # Escape 取消
        self.root.bind('<Escape>', lambda e: self.cancel_recording())
        
        # Ctrl+M 切换模式
        self.root.bind('<Control-m>', lambda e: self.toggle_mode())
    
    def toggle_mode(self):
        """切换识别模式"""
        if not QINIU_ASR_AVAILABLE:
            self.ui.show_error("七牛云ASR未配置，请安装qiniu模块")
            return
        
        self.use_cloud_api = not self.use_cloud_api
        mode = "云端高精度" if self.use_cloud_api else "本地Whisper"
        
        if self.use_cloud_api:
            # 估算成本对比
            cost_hint = " (约¥0.005/10秒)"
        else:
            cost_hint = " (零成本)"
        
        self.ui.set_status(f"已切换至: {mode}{cost_hint}")
        self.ui.update_mode_button(self.use_cloud_api)
    
    def _on_space_press(self, event):
        if str(event.widget) != str(self.root):
            return
        if not self.is_recording:
            self.start_recording()
    
    def _on_space_release(self, event):
        if str(event.widget) != str(self.root):
            return
        if self.is_recording:
            self.stop_recording()
    
    def _on_close(self):
        if self.is_recording:
            self.recognizer.is_recording = False
        self.root.destroy()
    
    def cancel_recording(self):
        if self.is_recording:
            self.recognizer.is_recording = False
            self.is_recording = False
            self.ui.set_recording_state(False)
            self.ui.set_status("已取消")
    
    def start_recording(self):
        if self.is_recording or not self.is_initialized:
            return
        
        try:
            self.is_recording = True
            self.ui.set_recording_state(True)
            
            mode = "云端" if self.use_cloud_api else "本地"
            self.ui.set_status(f"🎤 {mode}模式录音中，请说话...")
            
            thread = threading.Thread(target=self._record_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.is_recording = False
            self.ui.set_recording_state(False)
            self._handle_error("录音启动失败", e)
    
    def _record_thread(self):
        try:
            self.recognizer.start_recording()
        except Exception as e:
            self.root.after(0, lambda: self._handle_error("麦克风错误", e))
            self.root.after(0, lambda: self.ui.set_recording_state(False))
            self.is_recording = False
    
    def stop_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.ui.set_recording_state(False)
        self.ui.set_status("⏳ 正在处理...")
        
        thread = threading.Thread(target=self._recognize_thread)
        thread.daemon = True
        thread.start()
    
    def _recognize_thread(self):
        try:
            audio_data = self.recognizer.stop_recording()
            
            if audio_data is None or len(audio_data) == 0:
                self.root.after(0, lambda: self.ui.show_error("未检测到音频"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            duration = len(audio_data) / 16000
            
            # 根据模式选择识别引擎
            if self.use_cloud_api and self.qiniu_asr:
                self.ui.set_status(f"☁️ 七牛云ASR识别中 ({duration:.1f}s)...")
                # 注意：这里需要先将音频保存为文件再上传
                # 简化处理，实际使用请参考 qiniu_asr.py
                raw_text = f"[云端识别] {duration:.1f}秒音频\n请配置七牛云密钥启用云端模式"
            else:
                if duration > 30:
                    self.ui.set_status(f"📝 长语音模式 ({duration:.1f}s)...")
                    raw_text = self.recognizer.recognize_long_audio(audio_data)
                else:
                    self.ui.set_status("🔍 Whisper本地识别中...")
                    raw_text = self.recognizer.recognize(audio_data)
            
            if not raw_text:
                self.root.after(0, lambda: self.ui.show_error("未识别到文字"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            # 文本处理
            self.ui.set_status("✏️ 文本纠错中...")
            processed_text = self.processor.process(raw_text)
            
            # 更新UI
            self.current_text = processed_text
            self.root.after(0, lambda: self.ui.set_result(processed_text))
            
            mode = "云端" if self.use_cloud_api else "本地"
            self.root.after(0, lambda: self.ui.set_status(f"✅ {mode}识别完成"))
            self.root.after(3000, lambda: self.ui.set_status("就绪 | 可继续录音"))
            
        except Exception as e:
            self.root.after(0, lambda: self._handle_error("识别失败", e))
            self.root.after(0, lambda: self.ui.set_status("就绪"))
    
    def _handle_error(self, title: str, error: Exception):
        error_msg = str(error)
        if "permission" in error_msg.lower():
            self.ui.show_error("麦克风权限被拒绝")
        elif "device" in error_msg.lower():
            self.ui.show_error("未检测到麦克风")
        else:
            self.ui.show_error(f"{title}: {error_msg[:50]}")
    
    def _show_fatal_error(self, message: str):
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", message)
            root.destroy()
        except:
            print(f"FATAL ERROR: {message}")
    
    def copy_text(self):
        if self.current_text:
            try:
                pyperclip.copy(self.current_text)
                self.ui.set_status("📋 已复制到剪贴板 ✓")
                self.root.after(2000, lambda: self.ui.set_status("就绪"))
            except:
                self.ui.show_error("复制失败")
        else:
            self.ui.show_error("没有可复制的文本")
    
    def run(self):
        self.ui.set_status("就绪 | Ctrl+M 切换模式 | 空格键录音")
        self.root.mainloop()


def run_demo_mode(audio_file: str = "sample.wav"):
    """Demo演示模式"""
    print("=" * 50)
    print("🎬 语音输入法 Demo 演示模式")
    print("=" * 50)
    
    if not os.path.exists(audio_file):
        print(f"❌ 找不到示例音频: {audio_file}")
        print("   请创建 sample.wav 或指定其他音频文件")
        return
    
    print(f"\n📁 加载音频: {audio_file}")
    
    try:
        # 初始化识别器
        recognizer = WhisperRecognizer()
        processor = TextProcessor()
        
        # 加载音频
        import wave
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            audio_array = (wave.struct.unpack(f"{wf.getnframes()}h", frames))
            audio_data = recognizer.stop_recording.__self__
        
        print("\n🎤 开始识别...")
        print("-" * 30)
        
        # 模拟识别过程
        import time
        for i in range(3, 0, -1):
            print(f"   识别倒计时: {i}...")
            time.sleep(0.5)
        
        # 实际识别
        result = recognizer.recognize(recognizer.stop_recording.__self__)
        processed = processor.process(result)
        
        print("\n✅ 识别结果:")
        print("-" * 30)
        print(processed)
        print("-" * 30)
        print("\n🎬 Demo 演示完成!")
        
    except Exception as e:
        print(f"❌ Demo失败: {e}")


def main():
    if "--demo" in sys.argv:
        # Demo 模式
        audio_file = "sample.wav"
        if len(sys.argv) > 2:
            audio_file = sys.argv[2]
        run_demo_mode(audio_file)
    else:
        # GUI 模式
        try:
            app = VoiceInputApp()
            app.run()
        except KeyboardInterrupt:
            print("\n已退出")
        except Exception as e:
            print(f"启动失败: {e}")


if __name__ == "__main__":
    main()
