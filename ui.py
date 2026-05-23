#!/usr/bin/env python3
"""
语音输入法 UI 模块 V3
- 云端/本地模式切换按钮
- 快捷键提示
"""

import tkinter as tk
from tkinter import scrolledtext, font as tkfont


class VoiceInputUI:
    """语音输入法 UI V3"""
    
    def __init__(
        self,
        root: tk.Tk,
        on_record_start: callable,
        on_record_stop: callable,
        on_copy: callable,
        on_mode_switch: callable = None,
        use_cloud_api: bool = False,
        cloud_available: bool = False
    ):
        self.root = root
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_copy = on_copy
        self.on_mode_switch = on_mode_switch
        self.cloud_available = cloud_available
        
        self._setup_ui()
        self.update_mode_button(use_cloud_api)
    
    def _setup_ui(self):
        """设置 UI 组件"""
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # ===== 标题栏 =====
        header_frame = tk.Frame(main_frame, bg="#f8f9fa")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_font = tkfont.Font(family="Microsoft YaHei", size=18, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="🎤 语音输入法 V3",
            font=title_font,
            bg="#f8f9fa",
            fg="#1a1a2e"
        )
        title_label.pack(side=tk.LEFT)
        
        # 赛题标签
        contest_label = tk.Label(
            header_frame,
            text="七牛云×XEngineer",
            font=tkfont.Font(family="Arial", size=9),
            bg="#e8f5e9",
            fg="#2e7d32",
            padx=8,
            pady=2
        )
        contest_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # ===== 状态栏 =====
        status_frame = tk.Frame(main_frame, bg="#e3f2fd", padx=15, pady=8)
        status_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.status_label = tk.Label(
            status_frame,
            text="⏳ 加载中...",
            font=tkfont.Font(family="Microsoft YaHei", size=11),
            bg="#e3f2fd",
            fg="#1565c0",
            anchor="w"
        )
        self.status_label.pack(fill=tk.X)
        
        # ===== 控制按钮栏 =====
        control_frame = tk.Frame(main_frame, bg="#f8f9fa")
        control_frame.pack(pady=(0, 12))
        
        # 录音按钮
        self.record_button = tk.Button(
            control_frame,
            text="🎙️ 按住说话",
            font=tkfont.Font(family="Microsoft YaHei", size=13, weight="bold"),
            width=12,
            height=2,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            borderwidth=2,
            command=self._on_button_click,
            cursor="hand2"
        )
        self.record_button.pack(side=tk.LEFT, padx=6)
        
        # 模式切换按钮
        self.mode_button = tk.Button(
            control_frame,
            text="☁️ 切换云端",
            font=tkfont.Font(family="Microsoft YaHei", size=11),
            width=12,
            height=2,
            bg="#607d8b",
            fg="white",
            command=self._on_mode_click,
            cursor="hand2"
        )
        self.mode_button.pack(side=tk.LEFT, padx=6)
        
        # 复制按钮
        copy_button = tk.Button(
            control_frame,
            text="📋 复制",
            font=tkfont.Font(family="Microsoft YaHei", size=11),
            width=10,
            height=2,
            bg="#2196F3",
            fg="white",
            command=self._on_copy_click,
            cursor="hand2"
        )
        copy_button.pack(side=tk.LEFT, padx=6)
        
        # 清除按钮
        clear_button = tk.Button(
            control_frame,
            text="🗑️ 清除",
            font=tkfont.Font(family="Microsoft YaHei", size=11),
            width=10,
            height=2,
            bg="#9E9E9E",
            fg="white",
            command=self._on_clear_click,
            cursor="hand2"
        )
        clear_button.pack(side=tk.LEFT, padx=6)
        
        # ===== 结果区域 =====
        result_frame = tk.Frame(main_frame, bg="#f8f9fa")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 模式说明
        self.mode_info_label = tk.Label(
            result_frame,
            text="💡 本地Whisper：零成本·离线·隐私保护",
            font=tkfont.Font(family="Arial", size=9),
            bg="#fff8e1",
            fg="#ff8f00",
            anchor="w",
            padx=10,
            pady=3
        )
        self.mode_info_label.pack(fill=tk.X, pady=(0, 5))
        
        # 结果标签
        result_label = tk.Label(
            result_frame,
            text="📝 识别结果",
            font=tkfont.Font(family="Microsoft YaHei", size=11, weight="bold"),
            bg="#f8f9fa",
            fg="#333",
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(0, 3))
        
        # 文本框
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=tkfont.Font(family="Microsoft YaHei", size=12),
            width=68,
            height=12,
            wrap=tk.WORD,
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=12,
            pady=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # ===== 快捷键栏 =====
        hint_frame = tk.Frame(main_frame, bg="#eceff1")
        hint_frame.pack(fill=tk.X, pady=(10, 0))
        
        hints = [
            ("空格", "录音"),
            ("Ctrl+M", "切换模式"),
            ("Ctrl+Enter", "强制识别"),
            ("Esc", "取消")
        ]
        
        for i, (key, desc) in enumerate(hints):
            hint_label = tk.Label(
                hint_frame,
                text=f"{key}: {desc}",
                font=tkfont.Font(family="Arial", size=9),
                bg="#eceff1",
                fg="#546e7a",
                padx=10,
                pady=4
            )
            hint_label.pack(side=tk.LEFT)
            if i < len(hints) - 1:
                tk.Label(
                    hint_frame,
                    text="│",
                    font=tkfont.Font(family="Arial", size=9),
                    bg="#eceff1",
                    fg="#90a4ae"
                ).pack(side=tk.LEFT, padx=2)
    
    def _on_button_click(self):
        if self.record_button.cget("bg") == "#4CAF50":
            self.on_record_start()
        else:
            self.on_record_stop()
    
    def _on_mode_click(self):
        if self.on_mode_switch:
            self.on_mode_switch()
    
    def _on_copy_click(self):
        self.on_copy()
    
    def _on_clear_click(self):
        self.result_text.delete(1.0, tk.END)
    
    def update_mode_button(self, use_cloud: bool):
        """更新模式按钮状态"""
        if use_cloud:
            self.mode_button.config(
                text="💻 切换本地",
                bg="#4CAF50"
            )
            self.mode_info_label.config(
                text="☁️ 七牛云ASR：更高精度·需联网·¥0.005/10秒",
                bg="#e3f2fd",
                fg="#1976d2"
            )
        else:
            self.mode_button.config(
                text="☁️ 切换云端",
                bg="#607d8b"
            )
            self.mode_info_label.config(
                text="💡 本地Whisper：零成本·离线·隐私保护",
                bg="#fff8e1",
                fg="#ff8f00"
            )
    
    def set_recording_state(self, is_recording: bool):
        if is_recording:
            self.record_button.config(
                text="⏹️ 松开停止",
                bg="#F44336",
                relief=tk.SUNKEN
            )
            self.status_label.config(
                text="🔴 录音中... 说话后停顿自动结束",
                bg="#ffebee",
                fg="#c62828"
            )
        else:
            self.record_button.config(
                text="🎙️ 按住说话",
                bg="#4CAF50",
                relief=tk.RAISED
            )
            self.status_label.config(
                text="⏳ 处理中...",
                bg="#fff3e0",
                fg="#e65100"
            )
    
    def set_status(self, status: str):
        # 根据状态选择颜色
        if "完成" in status or "✓" in status:
            bg, fg = "#e8f5e9", "#2e7d32"
        elif "错误" in status or "失败" in status or "❌" in status:
            bg, fg = "#ffebee", "#c62828"
        elif "就绪" in status or "☁️" in status or "💡" in status:
            bg, fg = "#e3f2fd", "#1565c0"
        elif "录音" in status or "🔴" in status:
            bg, fg = "#ffebee", "#c62828"
        else:
            bg, fg = "#fff3e0", "#e65100"
        
        self.status_label.config(text=status, bg=bg, fg=fg)
    
    def set_result(self, text: str):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.tag_add(tk.SEL, "1.0", tk.END)
        self.result_text.focus_set()
    
    def show_error(self, message: str):
        self.set_status(f"❌ {message}")
        self.root.after(3000, lambda: self.set_status("就绪"))
    
    def show_success(self, message: str):
        self.set_status(f"✅ {message}")
        self.root.after(2000, lambda: self.set_status("就绪"))


def main():
    """测试函数"""
    root = tk.Tk()
    root.title("Voice Input Method - 测试 V3")
    root.geometry("650x520")
    
    def dummy_start():
        print("开始录音")
    
    def dummy_stop():
        print("停止录音")
    
    def dummy_copy():
        print("复制")
    
    def dummy_switch():
        print("切换模式")
    
    ui = VoiceInputUI(
        root=root,
        on_record_start=dummy_start,
        on_record_stop=dummy_stop,
        on_copy=dummy_copy,
        on_mode_switch=dummy_switch,
        use_cloud_api=False,
        cloud_available=True
    )
    
    ui.set_result("这是一段测试文本。Whisper语音识别Demo，支持VAD连续识别和云端/本地模式切换。\n\n本地模式：零成本、离线可用、隐私保护\n云端模式：更高精度、需联网、实时计费")
    ui.set_status("就绪 | Ctrl+M 切换模式")
    
    root.mainloop()


if __name__ == "__main__":
    main()
