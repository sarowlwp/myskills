---
name: semiconductor-daily
description: Generate semiconductor industry daily reports (morning and evening editions) with stock price monitoring, news aggregation, and email delivery. Use when user needs to create or send semiconductor industry daily briefings, including stock data, company news, market analysis, and trend forecasts.
---

# Semiconductor Daily Report Skill

Generate professional semiconductor industry daily reports with morning and evening editions.

## Overview

This skill creates comprehensive semiconductor industry reports including:
- Real-time stock price monitoring (INTC, NVDA, AMD, TSM, etc.)
- Industry news aggregation
- Market analysis and trend forecasts
- Professional PDF report generation
- Automated email delivery

## Editions

### Morning Edition (7:30 AM)
- Pre-market stock data
- Overnight news summary
- Market opening outlook
- Key events to watch

### Evening Edition (6:00 PM)
- Market close data
- Daily performance summary
- After-hours news
- Tomorrow's outlook

## Workflow

### 1. Fetch Stock Data

Run Finnhub monitor script:

```bash
cd /root/.openclaw/workspace && python3 -u scripts/finnhub_unified_monitor.py
```

Key tickers: INTC, NVDA, AMD, TSM, QCOM, AVGO

### 2. Fetch Industry News

Use news fetcher for semiconductor news:

```bash
python3 scripts/news_fetcher.py semiconductor
```

Keywords: Intel, NVIDIA, AMD, TSMC, chip, semiconductor, AI chip

### 3. Generate Report

Create HTML with:
- Stock price table
- Company news section
- Industry analysis
- Market outlook

### 4. Convert to PDF

```bash
node /root/.openclaw/workspace/scripts/html_to_pdf.js <input.html> <output.pdf>
```

### 5. Send Email

```bash
/root/.openclaw/workspace/skills/custom-smtp-sender/custom-smtp-sender send \
    --to <recipient> \
    --subject "Semiconductor Daily | <edition> | <date>" \
    --body "Report attached" \
    --attachments <pdf_file>
```

## Report Structure

### Morning Edition

1. **Header**: Title, date, edition type
2. **Stock Overview**: Price table with overnight changes
3. **Overnight News**: Key developments from US/Asia markets
4. **Today's Focus**: Events to watch
5. **Market Outlook**: Opening expectations

### Evening Edition

1. **Header**: Title, date, edition type
2. **Market Summary**: Daily performance table
3. **Company News**: Major developments
4. **Industry Analysis**: Trends and insights
5. **Tomorrow's Outlook**: Next day preview

## Content Guidelines

### Stock Data Table

| Ticker | Company | Price | Change | Change% | Volume | RSI |
|--------|---------|-------|--------|---------|--------|-----|
| INTC | Intel | $xx.xx | ±$x.xx | ±x.xx% | xxM | xx |

### News Sections

- **Intel**: Process technology, foundry business, AI PC
- **NVIDIA**: GPU architecture, data center, AI dominance
- **AMD**: CPU market share, AI accelerators, competition
- **Industry**: Policy, supply chain, technology trends

## Styling

- Blue theme (#1976d2) for headers
- Green for positive changes
- Red for negative changes
- Clean tables with borders
- Professional sans-serif fonts

## Assets

- `assets/morning_template.html` - Morning report template
- `assets/evening_template.html` - Evening report template

## Scripts

- `scripts/news_fetcher.py` - Industry news aggregator
- `scripts/generate_morning.py` - Morning report generator
- `scripts/generate_evening.py` - Evening report generator

## Example Usage

"Generate semiconductor morning report and send to sarowlwp@gmail.com"

1. Run finnhub_unified_monitor.py
2. Fetch semiconductor news
3. Generate morning edition HTML
4. Convert to PDF
5. Send email
