#!/usr/bin/env python3
"""
Voice Input Method - 主程序入口 V2
- VAD 连续识别
- 长语音处理
- 完善的错误处理
"""

import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip

from ui import VoiceInputUI
from whisper_recognizer import WhisperRecognizer
from text_processor import TextProcessor


class VoiceInputApp:
    """语音输入法主应用 V2"""
    
    def __init__(self):
        # 创建窗口
        self.root = tk.Tk()
        self.root.title("Voice Input Method - 语音输入法 V2")
        self.root.geometry("600x420")
        self.root.resizable(True, True)
        
        # 初始化模块
        try:
            self.recognizer = WhisperRecognizer()
            self.processor = TextProcessor()
        except Exception as e:
            self._show_fatal_error(f"初始化失败: {e}")
            raise
        
        # 初始化UI
        self.ui = VoiceInputUI(
            root=self.root,
            on_record_start=self.start_recording,
            on_record_stop=self.stop_recording,
            on_copy=self.copy_text
        )
        
        # 状态变量
        self.is_recording = False
        self.current_text = ""
        self.is_initialized = True
        
        # 绑定快捷键
        self._bind_shortcuts()
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        # 空格键按住/松开
        self.root.bind('<space>', self._on_space_press)
        self.root.bind('<KeyRelease-space>', self._on_space_release)
        
        # Ctrl+Enter 强制识别
        self.root.bind('<Control-Return>', lambda e: self.stop_recording())
        
        # Escape 取消录音
        self.root.bind('<Escape>', lambda e: self.cancel_recording())
    
    def _on_space_press(self, event):
        """空格键按下：开始录音"""
        # 忽略按钮区域的点击
        if str(event.widget) != str(self.root):
            return
        if not self.is_recording:
            self.start_recording()
    
    def _on_space_release(self, event):
        """空格键释放：停止录音"""
        if str(event.widget) != str(self.root):
            return
        if self.is_recording:
            self.stop_recording()
    
    def _on_close(self):
        """窗口关闭"""
        if self.is_recording:
            self.recognizer.is_recording = False
        self.root.destroy()
    
    def cancel_recording(self):
        """取消录音"""
        if self.is_recording:
            self.recognizer.is_recording = False
            self.is_recording = False
            self.ui.set_recording_state(False)
            self.ui.set_status("已取消")
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording or not self.is_initialized:
            return
        
        try:
            self.is_recording = True
            self.ui.set_recording_state(True)
            self.ui.set_status("🎤 正在录音，请说话...")
            
            # 在后台线程执行录音
            thread = threading.Thread(target=self._record_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.is_recording = False
            self.ui.set_recording_state(False)
            self._handle_error("录音启动失败", e)
    
    def _record_thread(self):
        """录音线程"""
        try:
            self.recognizer.start_recording()
        except Exception as e:
            self.root.after(0, lambda: self._handle_error("麦克风错误", e))
            self.root.after(0, lambda: self.ui.set_recording_state(False))
            self.is_recording = False
    
    def stop_recording(self):
        """停止录音并识别"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.ui.set_recording_state(False)
        self.ui.set_status("⏳ 正在处理...")
        
        # 在后台线程执行识别
        thread = threading.Thread(target=self._recognize_thread)
        thread.daemon = True
        thread.start()
    
    def _recognize_thread(self):
        """识别线程"""
        try:
            # 停止录音并获取音频数据
            audio_data = self.recognizer.stop_recording()
            
            if audio_data is None or len(audio_data) == 0:
                self.root.after(0, lambda: self.ui.show_error("未检测到音频，请重试"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            # 检查音频时长
            duration = len(audio_data) / 16000  # 采样率 16kHz
            print(f"音频时长: {duration:.2f}s")
            
            # 选择识别模式
            if duration > 30:
                self.ui.set_status(f"📝 长语音模式 ({duration:.1f}s)...")
                raw_text = self.recognizer.recognize_long_audio(audio_data)
            else:
                self.ui.set_status("🔍 Whisper 识别中...")
                raw_text = self.recognizer.recognize(audio_data)
            
            if not raw_text:
                self.root.after(0, lambda: self.ui.show_error("未识别到文字，请重试"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            # 文本处理
            self.ui.set_status("✏️ 文本纠错中...")
            processed_text = self.processor.process(raw_text)
            
            # 更新UI
            self.current_text = processed_text
            self.root.after(0, lambda: self.ui.set_result(processed_text))
            self.root.after(0, lambda: self.ui.set_status("✅ 识别完成"))
            
            # 3秒后恢复状态
            self.root.after(3000, lambda: self.ui.set_status("就绪 | 可继续录音"))
            
        except Exception as e:
            self.root.after(0, lambda: self._handle_error("识别失败", e))
            self.root.after(0, lambda: self.ui.set_status("就绪"))
    
    def _handle_error(self, title: str, error: Exception):
        """统一错误处理"""
        error_msg = str(error)
        
        # 用户友好的错误提示
        if "permission" in error_msg.lower() or "访问被拒绝" in error_msg:
            self.ui.show_error("麦克风权限被拒绝，请在系统设置中授权")
        elif "device" in error_msg.lower() or "设备" in error_msg:
            self.ui.show_error("未检测到麦克风设备")
        elif "timeout" in error_msg.lower() or "超时" in error_msg:
            self.ui.show_error("连接超时，请检查网络")
        else:
            self.ui.show_error(f"{title}: {error_msg[:50]}")
    
    def _show_fatal_error(self, message: str):
        """致命错误弹窗"""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", message)
            root.destroy()
        except:
            print(f"FATAL ERROR: {message}")
    
    def copy_text(self):
        """复制文本到剪贴板"""
        if self.current_text:
            try:
                pyperclip.copy(self.current_text)
                self.ui.set_status("📋 已复制到剪贴板 ✓")
                self.root.after(2000, lambda: self.ui.set_status("就绪"))
            except Exception as e:
                self.ui.show_error("复制失败，请手动选择文本")
        else:
            self.ui.show_error("没有可复制的文本")
    
    def run(self):
        """运行应用"""
        self.ui.set_status("就绪 | 按住空格键说话，或点击按钮\nCtrl+Enter 强制识别 | Esc 取消")
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = VoiceInputApp()
        app.run()
    except KeyboardInterrupt:
        print("\n已退出")
    except Exception as e:
        print(f"启动失败: {e}")


if __name__ == "__main__":
    main()
