# Voice Input Method - 语音输入法

七牛云 × XEngineer 暑期实训营 · 题目一

> 一款基于 Whisper 的轻量级语音输入法 Demo，帮助用户通过语音高效输入文本。

## 功能特性

- 🎤 **一键录音**：按住空格键或点击按钮开始/结束录音
- 🎯 **Whisper 识别**：本地离线运行，准确率高，支持中英文
- 🔧 **智能纠错**：基础拼音纠错 + 常用词补全
- 💨 **低延迟响应**：短语音优先，快速输出
- 📋 **一键复制**：识别结果可直接复制使用

## 技术方案

| 模块 | 技术选型 |
|------|----------|
| 语音识别 | OpenAI Whisper (base 模型) |
| 录音采集 | PyAudio |
| 文本纠错 | 拼音纠错 + 正则规则 |
| UI 界面 | Tkinter (Python 标准库) |
| 部署方式 | 本地运行，无需联网 |

## 环境要求

- Python 3.9+
- macOS / Windows / Linux
- 麦克风设备

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

Whisper 模型会在首次运行时自动下载（约140MB）。

### 3. 使用方法

1. **启动程序**：运行 `python main.py`
2. **开始录音**：
   - 按住 **空格键** 开始录音
   - 松开 **空格键** 结束录音
   - 或点击界面 **「按住说话」** 按钮
3. **等待识别**：录音结束后自动识别并显示结果
4. **复制使用**：点击「复制」按钮将文本复制到剪贴板

## 项目结构

```
voice-input-method/
├── main.py              # 主程序入口
├── whisper_recognizer.py # Whisper 语音识别模块
├── text_processor.py     # 文本纠错与处理
├── ui.py                 # Tkinter UI 界面
├── requirements.txt      # Python 依赖
└── README.md             # 项目说明
```

## 核心算法

### 语音识别流程

```
录音采集 → VAD降噪 → Whisper推理 → 标点恢复 → 纠错处理 → 输出文本
```

### 纠错策略

1. **谐音纠错**：常见拼音错误自动修正（如 "zhi shi" → "知识"）
2. **常用词补全**：根据上下文自动补全短语
3. **标点恢复**：基于语义添加适当标点

## 性能指标

| 指标 | 数值 |
|------|------|
| 英文识别准确率 | ~98% |
| 中文识别准确率 | ~95% |
| 平均延迟 | < 2s (短语音) |
| 模型内存占用 | ~140M (base) |

## 未来优化方向

- [ ] 支持长语音连续识别
- [ ] 方言识别模型
- [ ] 实时流式识别
- [ ] 快捷短语模板
- [ ] 移动端适配

## 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [七牛云](https://www.qiniu.com/) - 实训营平台
- [XEngineer](https://www.xengineer.com/) - 技术支持

## License

MIT License
