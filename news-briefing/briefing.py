#!/usr/bin/env python3
"""
新闻简报生成技能
支持历史记录去重、HTML/PDF生成和邮件发送
"""

import json
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# 配置
WORKRECORD_DIR = Path("/root/.openclaw/workspace/workrecord")
SKILL_DIR = Path("/root/.openclaw/workspace/skills/news-briefing")
SMTP_SENDER = "/root/.openclaw/workspace/skills/custom-smtp-sender/custom-smtp-sender"
HTML_TO_PDF = "/root/.openclaw/workspace/scripts/html_to_pdf.js"


class NewsBriefing:
    """新闻简报生成器"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.record_dir = WORKRECORD_DIR / topic
        self.history_file = self.record_dir / "history.json"
        self.max_days = 30
        
        # 确保目录存在
        self.record_dir.mkdir(parents=True, exist_ok=True)
    
    def load_history(self):
        """加载历史记录"""
        if not self.history_file.exists():
            return {"records": []}
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"records": []}
    
    def save_history(self, history):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def compute_hash(self, text: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    def is_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """判断两个标题是否相似"""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        if not words1 or not words2:
            return False
        intersection = words1 & words2
        union = words1 | words2
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def is_duplicate(self, title: str, summary: str = "") -> bool:
        """检查是否是重复新闻"""
        history = self.load_history()
        new_hash = self.compute_hash(title + summary)
        
        for record in history.get("records", []):
            if record.get("content_hash") == new_hash:
                return True
            if self.is_similar(record.get("title", ""), title):
                return True
        return False
    
    def add_record(self, title: str, source: str, summary: str = ""):
        """添加新记录"""
        history = self.load_history()
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "source": source,
            "content_hash": self.compute_hash(title + summary)
        }
        
        history["records"].append(record)
        
        # 清理旧记录
        cutoff_date = datetime.now() - timedelta(days=self.max_days)
        history["records"] = [
            r for r in history["records"]
            if datetime.fromisoformat(r["timestamp"]) > cutoff_date
        ]
        
        self.save_history(history)
        return True
    
    def filter_new_news(self, news_list: list) -> list:
        """过滤新闻列表，只返回未报道过的新闻"""
        new_news = []
        for news in news_list:
            title = news.get("title", "")
            summary = news.get("summary", "")
            
            if not self.is_duplicate(title, summary):
                new_news.append(news)
                self.add_record(title, news.get("source", ""), summary)
        
        return new_news
