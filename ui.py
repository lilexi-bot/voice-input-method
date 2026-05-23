#!/usr/bin/env python3
"""
语音输入法 UI 模块
基于 Tkinter 的图形界面
"""

import tkinter as tk
from tkinter import scrolledtext, font as tkfont


class VoiceInputUI:
    """语音输入法 UI"""
    
    def __init__(
        self,
        root: tk.Tk,
        on_record_start: callable,
        on_record_stop: callable,
        on_copy: callable
    ):
        """
        初始化 UI
        
        Args:
            root: Tkinter 根窗口
            on_record_start: 开始录音回调
            on_record_stop: 停止录音回调
            on_copy: 复制文本回调
        """
        self.root = root
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_copy = on_copy
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI 组件"""
        # 主容器
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_font = tkfont.Font(family="Arial", size=18, weight="bold")
        title_label = tk.Label(
            main_frame,
            text="🎤 语音输入法",
            font=title_font,
            bg="#f5f5f5",
            fg="#333"
        )
        title_label.pack(pady=(0, 10))
        
        # 副标题
        subtitle_font = tkfont.Font(family="Arial", size=10)
        subtitle_label = tk.Label(
            main_frame,
            text="基于 Whisper 的本地语音识别",
            font=subtitle_font,
            bg="#f5f5f5",
            fg="#666"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="就绪",
            font=tkfont.Font(family="Arial", size=11),
            bg="#f5f5f5",
            fg="#666"
        )
        self.status_label.pack(pady=(0, 15))
        
        # 录音按钮
        button_frame = tk.Frame(main_frame, bg="#f5f5f5")
        button_frame.pack(pady=(0, 20))
        
        self.record_button = tk.Button(
            button_frame,
            text="🎙️ 按住说话",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            borderwidth=3,
            command=self._on_button_click
        )
        self.record_button.pack(side=tk.LEFT, padx=10)
        
        # 复制按钮
        copy_button = tk.Button(
            button_frame,
            text="📋 复制",
            font=tkfont.Font(family="Arial", size=12),
            width=10,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self._on_copy_click
        )
        copy_button.pack(side=tk.LEFT, padx=10)
        
        # 清除按钮
        clear_button = tk.Button(
            button_frame,
            text="🗑️ 清除",
            font=tkfont.Font(family="Arial", size=12),
            width=10,
            height=2,
            bg="#9E9E9E",
            fg="white",
            command=self._on_clear_click
        )
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # 结果文本框
        result_frame = tk.Frame(main_frame, bg="#f5f5f5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        result_label = tk.Label(
            result_frame,
            text="识别结果:",
            font=tkfont.Font(family="Arial", size=11),
            bg="#f5f5f5",
            fg="#333",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 5))
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=tkfont.Font(family="Microsoft YaHei", size=12),
            width=60,
            height=10,
            wrap=tk.WORD,
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 提示标签
        hint_font = tkfont.Font(family="Arial", size=9)
        hint_label = tk.Label(
            main_frame,
            text="💡 提示: 按住空格键说话，松开自动识别",
            font=hint_font,
            bg="#f5f5f5",
            fg="#999"
        )
        hint_label.pack(pady=(10, 0))
    
    def _on_button_click(self):
        """按钮点击事件"""
        # 切换录音状态
        if self.record_button.cget("bg") == "#4CAF50":
            self.on_record_start()
        else:
            self.on_record_stop()
    
    def _on_copy_click(self):
        """复制按钮点击"""
        self.on_copy()
    
    def _on_clear_click(self):
        """清除按钮点击"""
        self.result_text.delete(1.0, tk.END)
    
    def set_recording_state(self, is_recording: bool):
        """设置录音状态"""
        if is_recording:
            self.record_button.config(
                text="⏹️ 松开停止",
                bg="#F44336"  # 红色
            )
            self.status_label.config(
                text="🔴 录音中...",
                fg="#F44336"
            )
        else:
            self.record_button.config(
                text="🎙️ 按住说话",
                bg="#4CAF50"  # 绿色
            )
            self.status_label.config(
                text="⏳ 处理中...",
                fg="#FF9800"
            )
    
    def set_status(self, status: str):
        """设置状态文本"""
        self.status_label.config(text=status, fg="#666")
    
    def set_result(self, text: str):
        """设置识别结果"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
    
    def show_error(self, message: str):
        """显示错误消息"""
        self.status_label.config(text=f"❌ {message}", fg="#F44336")
        # 3秒后恢复状态
        self.root.after(3000, lambda: self.set_status("就绪"))
    
    def show_success(self, message: str):
        """显示成功消息"""
        self.status_label.config(text=f"✅ {message}", fg="#4CAF50")
        self.root.after(2000, lambda: self.set_status("就绪"))


def main():
    """测试函数"""
    root = tk.Tk()
    root.title("Voice Input Method - 测试")
    root.geometry("600x450")
    
    def dummy_start():
        print("开始录音")
    
    def dummy_stop():
        print("停止录音")
    
    def dummy_copy():
        print("复制")
    
    ui = VoiceInputUI(
        root=root,
        on_record_start=dummy_start,
        on_record_stop=dummy_stop,
        on_copy=dummy_copy
    )
    
    # 模拟设置结果
    ui.set_result("这是一段测试文本，用于验证UI显示是否正常。")
    
    root.mainloop()


if __name__ == "__main__":
    main()
