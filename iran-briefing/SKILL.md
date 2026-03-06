---
name: iran-briefing
description: Generate Iran-US conflict briefing reports in Chinese with real-time news from kimi_search, PDF generation, and email delivery. Use when user needs to create or send Iran conflict situation reports in Chinese, including news aggregation from the last 3 hours, HTML/PDF formatting, and SMTP email sending.
---

# Iran Briefing Skill (伊朗简报)

生成专业的伊朗-美国冲突局势简报，使用中文输出，包含四个主要部分。

**可用工具**：kimi_search（搜索新闻）、exec（执行命令/脚本）

## 概述

本技能创建全面的伊朗局势简报，包括四个主要部分：
1. **动态总结** - 局势一句话概览
2. **最新事件** - 至少5条可信事件（标题、时间、来源、链接、中文摘要）
3. **各方表态** - 伊朗、美国、以色列、国际社会的最新表态
4. **金融及价格影响** - 大宗商品、股市、航运的影响分析

**所有输出内容为中文**

## 重要提示

**⚠️ 必须发送邮件**：生成报告后，**必须使用 exec 工具执行邮件发送脚本**，将PDF发送到指定邮箱（sarowlwp@gmail.com）。这是任务的强制要求，不可跳过。

**📋 执行日志记录**：每步操作必须记录到 workrecord 日志，格式为 `skill+log+时间`：
```
echo "iran-briefing+log+$(date +%Y-%m-%d-%H-%M)" >> /root/.openclaw/workspace/workrecord.log
```

**发送命令模板**：
```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/iran-briefing/scripts/send_email.py --to sarowlwp@gmail.com --subject '伊朗简报 | MM-DD HH:MM' --body '简报PDF已生成，请查看附件。' --attachments /tmp/iran_briefing.pdf"
}
```

**发送成功后**：
- 必须报告"邮件已成功发送到 sarowlwp@gmail.com"
- 确认发送的主题和附件文件名
- 如发送失败，必须重试并报告失败原因

---

## 工作流程

### 1. 获取实时新闻（必须使用 kimi_search）

**重要：使用 kimi_search 工具获取最近 3 小时内的新闻**

搜索查询（执行多个，确保获取足够覆盖3小时范围的最新新闻）：
```
kimi_search:
{
  "query": "Iran US Israel conflict latest news last 3 hours"
}
```

```
kimi_search:
{
  "query": "伊朗 美国 以色列 冲突 最新消息"
}
```

```
kimi_search:
{
  "query": "Gaza Hamas Hezbollah attack today"
}
```

**时间过滤要求**：
- 从搜索结果中**只选择发布时间 ≤ 3小时的新闻**
- **严格排除超过24小时（1天）的旧新闻**，即使出现在搜索结果中
- 优先选择最近1小时内的新闻，其次是1-3小时内的
- **确保最终整理至少10条新闻**：如果单次搜索结果不足，尝试更换关键词再次搜索

关键词：Iran, Israel, Gaza, Hamas, Hezbollah, Houthi, Middle East conflict, attack, strike

### 2. 整合新闻内容（中文）

**⚠️ 重要提示：必须从搜索结果中整理至少10条最新新闻事件**

将搜索结果整合为四个部分：

**第一部分：动态总结**
- 用一句话总结当前局势

**第二部分：最新事件（至少10条，必须达成）**
- 仔细阅读搜索结果，提取所有相关新闻
- 如果搜索结果超过10条，优先选择最新、最重要的10条以上
- 如果搜索结果不足10条，尝试更换搜索关键词再次搜索，直到凑齐至少10条
- 每条事件必须包含：标题（中文）、发生时间、来源、链接、中文摘要（100-150字）
每条事件包含：
- 标题（中文）
- 发生时间
- 来源（媒体名称）
- 链接（原文链接）
- 中文摘要（100-150字）

**第三部分：各方表态**
- 🇮🇷 伊朗方面（伊朗政府/军方/外交部表态）
- 🇺🇸 美国方面（美国政府/军方/白宫表态）
- 🇮🇱 以色列方面（以色列政府/军方表态）
- 🌍 国际社会（联合国/欧盟/中国/俄罗斯等表态）

**第四部分：金融及价格影响**
- 大宗商品价格（原油、黄金、天然气）
- 股市影响（美股、欧洲、亚太）
- 航运与物流（霍尔木兹海峡、航运成本）

### 3. 填充 HTML 模板

使用 `assets/template.html` 中的变量填充内容：

**模板变量：**
- `{{TIMESTAMP}}` - 生成时间
- `{{SUMMARY}}` - 动态总结
- `{{EVENT1_TITLE}}` 到 `{{EVENT10_SUMMARY}}` - 10条事件详情
- `{{IRAN_STATEMENT_PARTY}}` / `{{IRAN_STATEMENT_CONTENT}}` - 伊朗表态
- `{{US_STATEMENT_PARTY}}` / `{{US_STATEMENT_CONTENT}}` - 美国表态
- `{{ISRAEL_STATEMENT_PARTY}}` / `{{ISRAEL_STATEMENT_CONTENT}}` - 以色列表态
- `{{INTL_STATEMENT_PARTY}}` / `{{INTL_STATEMENT_CONTENT}}` - 国际表态
- `{{OIL_PRICE}}` / `{{OIL_CHANGE}}` / `{{OIL_IMPACT}}` - 原油价格及影响
- `{{GOLD_PRICE}}` / `{{GOLD_CHANGE}}` / `{{GOLD_IMPACT}}` - 黄金价格及影响
- `{{GAS_PRICE}}` / `{{GAS_CHANGE}}` / `{{GAS_IMPACT}}` - 天然气价格及影响
- `{{US_MARKET_IMPACT}}` / `{{EU_MARKET_IMPACT}}` / `{{ASIA_MARKET_IMPACT}}` - 股市影响
- `{{HORMUZ_IMPACT}}` / `{{SHIPPING_COST_IMPACT}}` - 航运影响

### 4. 转换为PDF并发送邮件（合并执行）

**使用合并脚本一次性完成PDF转换和邮件发送：**

```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/iran-briefing/scripts/convert_and_send.py /tmp/iran_briefing.html sarowlwp@gmail.com '伊朗简报 | MM-DD HH:MM'"
}
```

**替代方案（分开执行）**：
- 转换PDF：`node /root/.openclaw/workspace/skills/iran-briefing/scripts/html_to_pdf.js <input.html> <output.pdf>`
- 发送邮件：`python3 /root/.openclaw/workspace/skills/iran-briefing/scripts/send_email.py --to <recipient> --subject <subject> --attachments <pdf>`

## 报告结构（四个部分）

### 第一部分：动态总结
- 一句话概括当前局势
- 放在橙色背景框中

### 第二部分：最新事件（最近3小时）
- 至少10条可信事件
- 每条包含：标题、时间、来源、链接、中文摘要
- 绿色左侧边框

### 第三部分：各方表态
- 伊朗方面（伊朗政府/革命卫队/外交部）
- 美国方面（美国政府/国防部/白宫）
- 以色列方面（以色列政府/国防军）
- 国际社会（联合国/欧盟/中国/俄罗斯等）
- 绿色背景框

### 第四部分：金融及价格影响
- **大宗商品价格表**：原油、黄金、天然气
- **股市影响**：美股、欧洲、亚太
- **航运与物流**：霍尔木兹海峡、航运成本
- 蓝色背景框

## 样式指南

- **主标题**：红色 (#d32f2f)，居中
- **章节标题**：蓝色 (#1976d2)，左侧边框
- **动态总结**：橙色 (#ff9800) 背景
- **新闻事件**：绿色左侧边框
- **各方表态**：绿色背景
- **金融影响**：蓝色背景
- **风险预警**：红色 (#c62828) 背景
- **字体**：中文字体（Noto Sans SC, PingFang SC, Microsoft YaHei）

## 资源文件

- `assets/template.html` - HTML 报告模板（中文，四部分结构）

## 使用示例

### 示例：生成并发送伊朗简报

**用户请求**: "生成今天的伊朗简报并发送到 sarowlwp@gmail.com"

**完整执行流程**:

#### 步骤1：搜索最新新闻
使用 kimi_search 工具搜索最近3小时的新闻：
```
kimi_search:
{
  "query": "Iran US Israel conflict latest news last 3 hours 2026"
}
```

```
kimi_search:
{
  "query": "伊朗 美国 以色列 冲突 最新消息"
}
```

```
kimi_search:
{
  "query": "Gaza Hamas Hezbollah attack today"
}
```

#### 步骤2：整合新闻内容
将搜索结果整合为四个部分：
- **动态总结**：一句话概括当前局势
- **最新事件**：至少10条可信事件（含标题、时间、来源、链接、中文摘要）
- **各方表态**：伊朗、美国、以色列、国际社会
- **金融影响**：原油、黄金、股市、航运

#### 步骤3：生成HTML报告
填充 `assets/template.html` 模板中的变量，保存到 `/tmp/iran_briefing.html`

#### 步骤4：转换为PDF
使用 exec 工具执行转换脚本：
```
exec:
{
  "command": "node /root/.openclaw/workspace/skills/iran-briefing/scripts/html_to_pdf.js /tmp/iran_briefing.html /tmp/iran_briefing.pdf"
}
```

#### 步骤5：发送邮件（必须执行）
**重要：必须使用 exec 工具执行邮件发送脚本，将PDF发送到指定邮箱**
```
exec:
{
  "command": "python3 /root/.openclaw/workspace/skills/iran-briefing/scripts/send_email.py --to sarowlwp@gmail.com --subject '伊朗简报 | 03-06 12:00' --body '简报PDF已生成，请查看附件。' --attachments /tmp/iran_briefing.pdf"
}
```

**发送完成后报告结果**：
- 确认邮件已成功发送到 sarowlwp@gmail.com
- 报告简报的主要内容和关键动态

---

## 时间检查要求

**⏰ 执行前必须先获取当前系统时间**：
1. 调用 `session_status` 工具获取当前日期时间
2. **只使用发布时间 ≤ 3小时的新闻内容**
3. **严格排除超过24小时（1天）的旧新闻**
4. 在报告顶部明确标注："数据截止时间：[获取的系统时间]"

**📅 日期过滤规则**：
- 只使用最近 **3小时内** 发布的新闻
- **严格丢弃超过24小时（1天）的旧新闻**，即使搜索结果中有
- 如果搜索结果中没有最近3小时内的内容，必须在报告中注明"过去3小时内无重大新进展"

## 注意事项

- **必须使用 kimi_search** 获取最新新闻，而不是仅依赖 RSS
- **至少10条最新事件**，每条包含标题、时间、来源、链接、中文摘要
- **所有输出必须是中文**
- 新闻时间范围：**最近 3 小时内**（严格排除超过24小时的新闻）
- 邮件主题使用中文："伊朗简报 | MM-DD HH:MM"
