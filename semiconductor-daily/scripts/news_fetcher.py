#!/usr/bin/env python3
"""
News fetcher for semiconductor industry
Fetches real-time news from RSS feeds
"""
import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
import re
import socket

socket.setdefaulttimeout(5)

def fetch_rss(url, timeout=5):
    """Fetch RSS feed"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except:
        return None

def parse_rss(xml_content, max_items=5):
    """Parse RSS XML"""
    if not xml_content:
        return []
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall('.//item')[:max_items]:
            title = item.find('title')
            desc = item.find('description')
            items.append({
                'title': title.text if title is not None else 'No title',
                'description': desc.text if desc is not None else ''
            })
        return items
    except:
        return []

def clean_text(text):
    """Clean HTML and extra whitespace"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:200]

def get_semiconductor_news():
    """Get semiconductor industry news"""
    rss_urls = [
        ("https://www.techmeme.com/feed.xml", 5),
    ]
    
    all_news = []
    keywords = ['intel', 'nvidia', 'amd', 'tsmc', 'qualcomm', 'chip', 'semiconductor', 'processor', 'ai chip']
    
    for url, max_items in rss_urls:
        content = fetch_rss(url, timeout=5)
        if content:
            items = parse_rss(content, max_items=max_items)
            for item in items:
                title_lower = item['title'].lower()
                if any(kw in title_lower for kw in keywords):
                    all_news.append(item)
    
    return all_news[:5]

def format_news(news_items):
    """Format news for report"""
    if not news_items:
        return "No relevant news found."
    
    lines = ["Semiconductor Industry News\n"]
    for i, item in enumerate(news_items, 1):
        title = item['title']
        desc = clean_text(item['description'])
        lines.append(f"{i}. {title}")
        if desc:
            lines.append(f"   {desc}...")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    news = get_semiconductor_news()
    print(format_news(news))
