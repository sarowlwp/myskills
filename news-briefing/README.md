# News Briefing Skill

新闻简报生成技能，支持历史记录去重、HTML/PDF 生成和邮件发送。

## 功能

- 历史记录管理（去重）
- HTML 简报生成
- PDF 转换
- 邮件发送

## 使用方法

```bash
# 生成简报
python3 /root/.openclaw/workspace/skills/news-briefing/briefing.py \
  --topic "iran" \
  --search "Iran US conflict latest news" \
  --search "伊朗 美国 冲突 最新消息" \
  --to sarowlwp@gmail.com \
  --subject "🔴 伊朗局势简报"
```

## 配置

在 `config.json` 中配置简报参数：

```json
{
  "iran": {
    "name": "伊朗局势简报",
    "search_queries": [
      "Iran US conflict latest news last 2 hours",
      "Trump Iran attack today",
      "伊朗 美国 冲突 最新消息"
    ],
    "schedule": "0 */2 * * *",
    "recipient": "sarowlwp@gmail.com",
    "subject_prefix": "🔴 伊朗局势简报"
  }
}
```

## 历史记录

历史记录存储在 `workrecord/{topic}/history.json`

格式：
```json
{
  "records": [
    {
      "timestamp": "2026-03-04T11:28:00",
      "title": "新闻标题",
      "source": "来源",
      "content_hash": "md5_hash"
    }
  ]
}
```

## 依赖

- Python 3.8+
- Node.js (用于 PDF 转换)
- Playwright (已随 OpenClaw 安装)
