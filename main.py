#!/usr/bin/env python3
"""
Voice Input Method - 主程序入口
七牛云 × XEngineer 暑期实训营 · 题目一
"""

import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip

from ui import VoiceInputUI
from whisper_recognizer import WhisperRecognizer
from text_processor import TextProcessor


class VoiceInputApp:
    """语音输入法主应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Input Method - 语音输入法")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 初始化模块
        self.recognizer = WhisperRecognizer()
        self.processor = TextProcessor()
        
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
        
        # 绑定空格键事件
        self.root.bind('<space>', self._on_space_press)
        self.root.bind('<KeyRelease-space>', self._on_space_release)
        
    def _on_space_press(self, event):
        """空格键按下：开始录音"""
        if not self.is_recording:
            self.start_recording()
    
    def _on_space_release(self, event):
        """空格键释放：停止录音"""
        if self.is_recording:
            self.stop_recording()
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.ui.set_recording_state(True)
        
        # 在后台线程执行录音
        thread = threading.Thread(target=self._record_thread)
        thread.daemon = True
        thread.start()
    
    def _record_thread(self):
        """录音线程"""
        try:
            self.recognizer.start_recording()
        except Exception as e:
            self.root.after(0, lambda: self.ui.show_error(f"录音启动失败: {e}"))
            self.root.after(0, lambda: self.ui.set_recording_state(False))
            self.is_recording = False
    
    def stop_recording(self):
        """停止录音并识别"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.ui.set_recording_state(False)
        
        # 在后台线程执行识别
        thread = threading.Thread(target=self._recognize_thread)
        thread.daemon = True
        thread.start()
    
    def _recognize_thread(self):
        """识别线程"""
        try:
            self.ui.set_status("正在识别...")
            
            # 停止录音并获取音频数据
            audio_data = self.recognizer.stop_recording()
            
            if audio_data is None or len(audio_data) == 0:
                self.root.after(0, lambda: self.ui.show_error("未检测到音频，请重试"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            # Whisper 识别
            self.ui.set_status("Whisper 识别中...")
            raw_text = self.recognizer.recognize(audio_data)
            
            if not raw_text:
                self.root.after(0, lambda: self.ui.show_error("未识别到文字，请重试"))
                self.root.after(0, lambda: self.ui.set_status("就绪"))
                return
            
            # 文本处理
            self.ui.set_status("文本纠错中...")
            processed_text = self.processor.process(raw_text)
            
            # 更新UI
            self.current_text = processed_text
            self.root.after(0, lambda: self.ui.set_result(processed_text))
            self.root.after(0, lambda: self.ui.set_status("识别完成"))
            
        except Exception as e:
            self.root.after(0, lambda: self.ui.show_error(f"识别失败: {e}"))
            self.root.after(0, lambda: self.ui.set_status("就绪"))
    
    def copy_text(self):
        """复制文本到剪贴板"""
        if self.current_text:
            pyperclip.copy(self.current_text)
            self.ui.set_status("已复制到剪贴板 ✓")
        else:
            self.ui.show_error("没有可复制的文本")
    
    def run(self):
        """运行应用"""
        self.ui.set_status("就绪 | 按住空格键说话，或点击「按住说话」按钮")
        self.root.mainloop()


def main():
    """主函数"""
    app = VoiceInputApp()
    app.run()


if __name__ == "__main__":
    main()
