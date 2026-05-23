#!/usr/bin/env python3
"""
语音输入法 UI 模块 V2
增强版界面，支持状态提示和快捷键显示
"""

import tkinter as tk
from tkinter import scrolledtext, font as tkfont


class VoiceInputUI:
    """语音输入法 UI V2"""
    
    def __init__(
        self,
        root: tk.Tk,
        on_record_start: callable,
        on_record_stop: callable,
        on_copy: callable
    ):
        """初始化 UI"""
        self.root = root
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_copy = on_copy
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI 组件"""
        # 主容器
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # ===== 标题区域 =====
        title_frame = tk.Frame(main_frame, bg="#f8f9fa")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_font = tkfont.Font(family="Microsoft YaHei", size=18, weight="bold")
        title_label = tk.Label(
            title_frame,
            text="🎤 语音输入法 V2",
            font=title_font,
            bg="#f8f9fa",
            fg="#1a1a2e"
        )
        title_label.pack(side=tk.LEFT)
        
        # 版本标签
        version_label = tk.Label(
            title_frame,
            text="VAD + 长语音版",
            font=tkfont.Font(family="Arial", size=9),
            bg="#e3f2fd",
            fg="#1976d2",
            padx=8,
            pady=2
        )
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # ===== 状态区域 =====
        status_frame = tk.Frame(main_frame, bg="#fff3e0", padx=15, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="⏳ 加载中...",
            font=tkfont.Font(family="Microsoft YaHei", size=11),
            bg="#fff3e0",
            fg="#e65100",
            anchor="w"
        )
        self.status_label.pack(fill=tk.X)
        
        # ===== 按钮区域 =====
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(pady=(0, 15))
        
        # 录音按钮
        self.record_button = tk.Button(
            button_frame,
            text="🎙️ 按住说话",
            font=tkfont.Font(family="Microsoft YaHei", size=13, weight="bold"),
            width=14,
            height=2,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            borderwidth=2,
            command=self._on_button_click,
            cursor="hand2"
        )
        self.record_button.pack(side=tk.LEFT, padx=8)
        
        # 复制按钮
        copy_button = tk.Button(
            button_frame,
            text="📋 复制",
            font=tkfont.Font(family="Microsoft YaHei", size=12),
            width=10,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self._on_copy_click,
            cursor="hand2"
        )
        copy_button.pack(side=tk.LEFT, padx=8)
        
        # 清除按钮
        clear_button = tk.Button(
            button_frame,
            text="🗑️ 清除",
            font=tkfont.Font(family="Microsoft YaHei", size=12),
            width=10,
            height=2,
            bg="#9E9E9E",
            fg="white",
            command=self._on_clear_click,
            cursor="hand2"
        )
        clear_button.pack(side=tk.LEFT, padx=8)
        
        # ===== 结果区域 =====
        result_frame = tk.Frame(main_frame, bg="#f8f9fa")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        result_label = tk.Label(
            result_frame,
            text="📝 识别结果",
            font=tkfont.Font(family="Microsoft YaHei", size=11, weight="bold"),
            bg="#f8f9fa",
            fg="#333",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 5))
        
        # 文本框
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=tkfont.Font(family="Microsoft YaHei", size=12),
            width=65,
            height=12,
            wrap=tk.WORD,
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=12,
            pady=10,
            spacing1=3,
            spacing2=2
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # ===== 底部提示 =====
        hint_frame = tk.Frame(main_frame, bg="#f8f9fa")
        hint_frame.pack(fill=tk.X, pady=(10, 0))
        
        hints = [
            ("空格键", "按住录音"),
            ("Ctrl+Enter", "强制识别"),
            ("Esc", "取消"),
            ("VAD", "自动检测")
        ]
        
        for i, (key, desc) in enumerate(hints):
            hint_label = tk.Label(
                hint_frame,
                text=f"{key}: {desc}",
                font=tkfont.Font(family="Arial", size=9),
                bg="#eceff1",
                fg="#546e7a",
                padx=8,
                pady=3
            )
            hint_label.pack(side=tk.LEFT, padx=3)
            if i < len(hints) - 1:
                tk.Label(
                    hint_frame,
                    text="|",
                    font=tkfont.Font(family="Arial", size=9),
                    bg="#f8f9fa",
                    fg="#b0bec5"
                ).pack(side=tk.LEFT, padx=0)
    
    def _on_button_click(self):
        """按钮点击事件"""
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
                bg="#F44336",
                relief=tk.SUNKEN
            )
            self.status_label.config(
                text="🔴 录音中... 说话后停顿自动结束",
                fg="#c62828",
                bg="#ffebee"
            )
        else:
            self.record_button.config(
                text="🎙️ 按住说话",
                bg="#4CAF50",
                relief=tk.RAISED
            )
            self.status_label.config(
                text="⏳ 处理中...",
                fg="#e65100",
                bg="#fff3e0"
            )
    
    def set_status(self, status: str):
        """设置状态文本"""
        # 根据状态内容选择颜色
        if "完成" in status or "✓" in status:
            bg, fg = "#e8f5e9", "#2e7d32"
        elif "错误" in status or "失败" in status:
            bg, fg = "#ffebee", "#c62828"
        elif "就绪" in status:
            bg, fg = "#e3f2fd", "#1565c0"
        else:
            bg, fg = "#fff3e0", "#e65100"
        
        self.status_label.config(text=status, bg=bg, fg=fg)
    
    def set_result(self, text: str):
        """设置识别结果"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        
        # 选中文本方便用户直接复制
        self.result_text.tag_add(tk.SEL, "1.0", tk.END)
        self.result_text.focus_set()
    
    def show_error(self, message: str):
        """显示错误消息"""
        self.set_status(f"❌ {message}")
        # 自动恢复
        self.root.after(3000, lambda: self.set_status("就绪"))
    
    def show_success(self, message: str):
        """显示成功消息"""
        self.set_status(f"✅ {message}")
        self.root.after(2000, lambda: self.set_status("就绪"))


def main():
    """测试函数"""
    root = tk.Tk()
    root.title("Voice Input Method - 测试 V2")
    root.geometry("620x500")
    
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
    
    ui.set_result("这是一段测试文本，用于验证UI显示是否正常。Whisper语音识别Demo，支持VAD连续识别和长语音处理。")
    ui.set_status("就绪 | 按空格键说话")
    
    root.mainloop()


if __name__ == "__main__":
    main()
