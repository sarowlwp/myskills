---
name: semiconductor-daily
description: 生成半导体行业中文早晚报，包含 Finnhub 实时股价、Kimi 搜索最新新闻、Reddit 社区监控，支持 PDF 生成和邮件发送。
tools:
  - type: function
    function:
      name: kimi_search
      description: 搜索最近 3 小时的实时新闻。
      parameters:
        type: object
        properties:
          query:
            type: string
            description: 搜索词
        required: ["query"]

  - type: function
    function:
      name: exec
      description: 执行系统命令，如运行Python脚本、Node脚本或发送邮件。
      parameters:
        type: object
        properties:
          command:
            type: string
            description: 完整的 shell 命令
        required: ["command"]
---

# 半导体行业早晚报 (Semiconductor Daily Report)

生成专业的半导体行业中文早晚报，整合多源数据。

## 概述

本技能创建全面的半导体行业报告，包括：
- **实时股价数据** — 使用 Finnhub API 获取准确股价
- **最新行业新闻** — 使用 kimi_search 搜索最近3日内新闻
- **Reddit 社区监控** — 关注 r/wallstreetbets, r/stocks, r/semiconductors 等板块的讨论
- **专业 PDF 报告生成**
- **自动邮件发送**

## 版本

### 早报 (07:30)
- 盘前股价数据
- 隔夜美股/亚洲市场动态
- 今日重点关注
- 开盘展望

### 晚报 (18:00)
- 收盘股价数据
- 当日新闻汇总
- Reddit 热门讨论
- 明日展望

## 重要提示

**⚠️ 必须发送邮件**：生成报告后，**必须使用 exec 工具执行邮件发送脚本**，将PDF发送到指定邮箱（sarowlwp@gmail.com）。这是任务的强制要求，不可跳过。

**📋 执行日志记录**：每步操作必须记录到 workrecord 日志，格式为 `skill+log+时间`：
```
echo "semiconductor-daily+log+$(date +%Y-%m-%d-%H-%M)" >> /root/.openclaw/workspace/workrecord.log
```

**发送命令模板**：
```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/send_email.py --to sarowlwp@gmail.com --subject '半导体早报 | MM-DD' --body '报告PDF已生成，请查看附件。' --attachments /tmp/semiconductor_morning.pdf"
}
```

**发送成功后**：
- 必须报告"邮件已成功发送到 sarowlwp@gmail.com"
- 确认发送的主题和附件文件名
- 如发送失败，必须重试并报告失败原因

---

## 工作流程

### 1. 获取股价数据 (Finnhub)

**必须使用 Finnhub API 获取准确股价数据**

运行股价监控脚本（使用 skill 目录下的脚本，确保 cron 环境可访问）：
```bash
python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/finnhub_unified_monitor.py
```

或者直接执行（脚本会自动处理工作目录）：
```bash
exec: /root/.openclaw/workspace/skills/semiconductor-daily/scripts/finnhub_unified_monitor.py
```

监控股票列表：
| 代码 | 公司 | 说明 |
|------|------|------|
| INTC | 英特尔 | CPU/代工 |
| NVDA | 英伟达 | GPU/AI芯片 |
| AMD | 超微 | CPU/GPU |
| TSM | 台积电 | 晶圆代工 |
| QCOM | 高通 | 移动芯片 |
| AVGO | 博通 | 网络芯片 |
| MU | 美光 | 存储芯片 |
| ASML | ASML | 光刻机 |
| ARM | ARM | 芯片架构 |
| AMAT | 应用材料 | 设备 |

### 2. 搜索行业新闻 (kimi_search)

**必须使用 kimi_search 搜索最近3日内新闻**

搜索查询（执行多个）：
```
kimi_search:
{
  "query": "Intel NVIDIA AMD TSMC semiconductor stock news last 3 days",
  "freshness": "pd3"
}
```

```
kimi_search:
{
  "query": "英特尔 英伟达 AMD 台积电 半导体 芯片 最新消息",
  "freshness": "pd3"
}
```

```
kimi_search:
{
  "query": "AI chip GPU data center earnings news today",
  "freshness": "pd3"
}
```

关键词：Intel, NVIDIA, AMD, TSMC, semiconductor, chip, AI chip, GPU, data center, earnings

### 3. 监控 Reddit (kimi_search)

**使用 kimi_search 搜索 Reddit 最近3日内热门讨论，并将内容翻译成中文**

搜索查询：
```
kimi_search:
{
  "query": "site:reddit.com/r/wallstreetbets Intel NVIDIA AMD semiconductor stock last 3 days",
  "freshness": "pd3"
}
```

```
kimi_search:
{
  "query": "site:reddit.com/r/stocks INTC NVDA AMD TSM investment discussion last 3 days",
  "freshness": "pd3"
}
```

```
kimi_search:
{
  "query": "site:reddit.com/r/semiconductors chip industry news discussion last 3 days",
  "freshness": "pd3"
}
```

**Reddit 内容处理要求：**
- 将英文帖子标题和内容翻译成中文
- 提取关键观点和情绪倾向（看涨/看跌/中性）
- 标注点赞数和评论数
- 按热门程度排序，优先展示高互动帖子

关注板块：r/wallstreetbets, r/stocks, r/semiconductors, r/investing, r/technology

### 4. 生成报告

整合数据生成中文报告：
- 股价表格（中文公司名，含成交量及成交量趋势分析）
- 新闻摘要（中文）
- Reddit 热门讨论（中文翻译/摘要，含点赞数、评论数、情绪倾向）
- 分析与展望（中文）

**成交量趋势分析要求：**
- 对比当日成交量与20日平均成交量
- 标注放量（>120%均值）或缩量（<80%均值）
- 分析成交量与价格变动的配合关系

### 5. 转换为PDF并发送邮件（合并执行）

**使用合并脚本一次性完成PDF转换和邮件发送：**

```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/convert_and_send.py /tmp/semiconductor_morning.html sarowlwp@gmail.com '半导体早报 | MM-DD'"
}
```

**替代方案（分开执行）**：
- 转换PDF：`node /root/.openclaw/workspace/skills/semiconductor-daily/scripts/html_to_pdf.js <input.html> <output.pdf>`
- 发送邮件：`python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/send_email.py --to <recipient> --subject <subject> --attachments <pdf>`

## 报告结构

### 早报

1. **标题区**：半导体早报 | 日期 | 盘前
2. **股价概览**：中英文对照表格，含涨跌幅、成交量及成交量趋势分析（放量/缩量标识）
3. **隔夜动态**：美股/亚洲市场重要新闻（中文摘要）
4. **今日关注**：重要事件提醒
5. **开盘展望**：技术面/资金面简评

### 晚报

1. **标题区**：半导体晚报 | 日期 | 收盘
2. **收盘数据**：当日涨跌排行，含成交量及成交量趋势分析（放量/缩量标识）
3. **新闻汇总**：当日重要新闻（分类：Intel/NVIDIA/AMD/行业）
4. **Reddit热议**：社区热门讨论摘要（中文翻译，含点赞数、评论数、情绪倾向）
5. **明日展望**：次日关注要点

## 样式指南

- **主标题**：深蓝色 (#1565c0)
- **章节标题**：左侧边框 + 蓝色
- **上涨**：绿色 (#2e7d32)
- **下跌**：红色 (#c62828)
- **新闻区块**：浅灰背景 + 左侧边框
- **Reddit区块**：橙色 (#e65100) 标识
- **字体**：中文字体优先（Noto Sans SC, PingFang SC, Microsoft YaHei）

## 资源文件

- `assets/morning_template.html` — 早报模板（中文）
- `assets/evening_template.html` — 晚报模板（中文）

## 使用示例

### 示例：生成并发送半导体早报

**用户请求**: "生成今天的半导体早报并发送到 sarowlwp@gmail.com"

**完整执行流程**:

#### 步骤1：获取实时股价数据
使用 exec 工具执行股价监控脚本：
```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/finnhub_unified_monitor.py"
}
```

#### 步骤2：搜索最新行业新闻
使用 kimi_search 工具搜索多条查询：
```
kimi_search:
{
  "query": "Intel NVIDIA AMD TSMC semiconductor stock news last 3 days"
}
```

```
kimi_search:
{
  "query": "英特尔 英伟达 AMD 台积电 半导体 芯片 最新消息"
}
```

#### 步骤3：搜索 Reddit 热门讨论
```
kimi_search:
{
  "query": "site:reddit.com/r/wallstreetbets Intel NVIDIA AMD semiconductor stock last 3 days"
}
```

#### 步骤4：生成HTML报告
整合上述数据，填充 `assets/morning_template.html` 模板，保存到 `/tmp/semiconductor_morning.html`

#### 步骤5：转换为PDF并发送邮件
使用合并脚本一次性完成PDF转换和邮件发送：
```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/semiconductor-daily/scripts/convert_and_send.py /tmp/semiconductor_morning.html sarowlwp@gmail.com '半导体早报 | 03-06'"
}
```

**发送完成后报告结果**：
- 确认邮件已成功发送到 sarowlwp@gmail.com
- 报告生成的股票数据和主要新闻摘要

---

## 注意事项

- **股价数据必须使用 Finnhub**，确保准确性
- **新闻和 Reddit 必须使用 kimi_search**，搜索最近3日内内容
- **所有输出内容为中文**
- 邮件主题使用中文："半导体早报/晚报 | MM-DD"
