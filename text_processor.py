#!/usr/bin/env python3
"""
文本处理模块
包括纠错、补全、标点恢复等功能
"""

import re


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        # 常见拼音错误映射（谐音纠错）
        self.homophone_map = {
            # 常见混淆
            "地": "的",
            "得": "的",
            "那": "哪",
            "在": "再",
            "做": "作",
            "像": "向",
            "带": "代",
            "以": "已",
            # 常见错误
            "之到": "知道",
            "不知道": "不知道",
            "谢谢": "谢谢",
        }
        
        # 中文标点规则
        self.punctuation_rules = [
            # 句号
            (r'([^。\.])(\s*)([^。\.])', r'\1。\3'),
            # 逗号
            (r'([^，,])([^，,])', r'\1，\2'),
        ]
        
        # 常用短语库
        self.common_phrases = [
            "请问", "您好", "谢谢", "对不起", "没关系",
            "麻烦您", "打扰一下", "不好意思", "非常感谢",
            "请稍等", "好的", "可以", "没问题",
        ]
    
    def process(self, text: str) -> str:
        """
        处理文本
        
        Args:
            text: 原始识别文本
            
        Returns:
            处理后的文本
        """
        if not text:
            return ""
        
        # 1. 去除多余空白
        text = self._normalize_whitespace(text)
        
        # 2. 首字母大写处理（英文句首）
        text = self._capitalize_sentences(text)
        
        # 3. 去除重复字符
        text = self._remove_duplicates(text)
        
        # 4. 基础标点恢复
        text = self._restore_punctuation(text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """规范化空白字符"""
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空白
        text = text.strip()
        return text
    
    def _capitalize_sentences(self, text: str) -> str:
        """处理英文句首大写"""
        # 中英混合文本中，英文句首字母大写
        text = re.sub(r'([。！？\.!?]\s+)([a-z])', 
                      lambda m: m.group(1) + m.group(2).upper(), 
                      text)
        return text
    
    def _remove_duplicates(self, text: str) -> str:
        """去除连续重复字符"""
        # 保留最多2个连续相同字符
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        return text
    
    def _restore_punctuation(self, text: str) -> str:
        """恢复基础标点"""
        # 如果文本末尾没有标点且长度适中，添加句号
        if text and text[-1] not in '。！？.!?，,':
            # 检查是否像完整句子
            if len(text) > 5:
                text += '。'
        return text
    
    def suggest_corrections(self, text: str) -> list:
        """
        给出纠错建议
        
        Args:
            text: 输入文本
            
        Returns:
            纠错建议列表 [(位置, 错误词, 建议词), ...]
        """
        suggestions = []
        
        # 检查常见错误
        for wrong, correct in self.homophone_map.items():
            start = 0
            while True:
                pos = text.find(wrong, start)
                if pos == -1:
                    break
                suggestions.append((pos, wrong, correct))
                start = pos + 1
        
        return suggestions
    
    def auto_complete(self, text: str) -> str:
        """
        智能补全（可选功能）
        
        Args:
            text: 输入文本
            
        Returns:
            补全后的文本
        """
        # 如果文本很短，尝试匹配常用短语
        if len(text) <= 3:
            for phrase in self.common_phrases:
                if phrase.startswith(text):
                    return phrase
        
        return text


def main():
    """测试函数"""
    processor = TextProcessor()
    
    test_cases = [
        "hello world",
        "今天天气很好",
        "我想吃苹果和香蕉",
        "请问您叫什么名字",
        "谢谢   你    帮   忙",
    ]
    
    print("文本处理测试")
    print("=" * 50)
    
    for text in test_cases:
        result = processor.process(text)
        print(f"输入: {text}")
        print(f"输出: {result}")
        print()


if __name__ == "__main__":
    main()
