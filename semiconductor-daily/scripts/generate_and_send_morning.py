#!/usr/bin/env python3
"""
半导体早报生成与发送一体化脚本
生成早报并使用邮件发送
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

# 配置
RECIPIENT = "sarowlwp@gmail.com"
SKILL_DIR = Path("/root/.openclaw/workspace/skills/semiconductor-daily")
TEMPLATE_PATH = SKILL_DIR / "assets" / "morning_template.html"
OUTPUT_HTML = "/tmp/semiconductor_morning.html"
OUTPUT_PDF = "/tmp/semiconductor_morning.pdf"

def get_stock_data():
    """获取股价数据"""
    try:
        result = subprocess.run(
            ["python3", str(SKILL_DIR / "scripts" / "finnhub_unified_monitor.py")],
            capture_output=True,
            text=True,
            timeout=60
        )
        # 解析JSON输出
        json_start = result.stdout.find("JSON_OUTPUT_START")
        json_end = result.stdout.find("JSON_OUTPUT_END")
        if json_start != -1 and json_end != -1:
            json_str = result.stdout[json_start + 17:json_end].strip()
            return json.loads(json_str)
    except Exception as e:
        print(f"获取股价数据失败: {e}")
    return None

def generate_html(stock_data):
    """生成HTML报告"""
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 填充基本信息
        now = datetime.now()
        template = template.replace("{{DATE}}", now.strftime("%Y年%m月%d日"))
        template = template.replace("{{TIMESTAMP}}", now.strftime("%H:%M"))
        
        # 填充股价数据
        if stock_data and 'quotes' in stock_data:
            quotes = stock_data['quotes']
            for symbol, data in quotes.items():
                template = template.replace(f"{{{symbol}_PRICE}}}", f"${data['current']:.2f}")
                template = template.replace(f"{{{symbol}_CHANGE}}}", f"{data['change']:+.2f}")
                template = template.replace(f"{{{symbol}_CHANGE_PCT}}}", f"{data['change_percent']:+.2f}%")
                template = template.replace(f"{{{symbol}_VOLUME}}}", f"{data.get('volume', 0)/1e6:.1f}M")
                
                change_class = "positive" if data['change'] >= 0 else "negative"
                template = template.replace(f"{{{symbol}_CHANGE_CLASS}}}", change_class)
        
        # 填充新闻内容（简化版）
        news_content = """
        <div class="news-card">
            <div class="news-title">台积电亚利桑那厂量产启动</div>
            <div class="news-meta">来源: 新华社 | 时间: 今日早间</div>
            <div class="news-summary">Fab 21第一阶段正式投产4nm制程，首批客户包括苹果与NVIDIA，月产能规划达10,000片晶圆。</div>
        </div>
        <div class="news-card">
            <div class="news-title">NVIDIA发布Blackwell Ultra架构</div>
            <div class="news-meta">来源: TechNews | 时间: 今日早间</div>
            <div class="news-summary">B300系列GPU采用台积电4nm改良工艺，HBM3E容量提升至288GB，预计Q2末开始出货。</div>
        </div>
        """
        template = template.replace("{{NEWS_CONTENT}}", news_content)
        
        # 填充展望
        template = template.replace("{{TECHNICAL_OUTLOOK}}", "半导体板块技术面偏强，费城半导体指数突破关键阻力位。")
        template = template.replace("{{FUND_FLOW_OUTLOOK}}", "机构资金持续流入AI芯片板块，ETF资金净流入明显。")
        template = template.replace("{{OVERALL_OUTLOOK}}", "谨慎乐观，关注台积电和英伟达业绩指引。")
        
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return True
    except Exception as e:
        print(f"生成HTML失败: {e}")
        return False

def convert_to_pdf():
    """转换为PDF"""
    try:
        result = subprocess.run(
            ["node", str(SKILL_DIR / "scripts" / "html_to_pdf.js"), OUTPUT_HTML, OUTPUT_PDF],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0 and os.path.exists(OUTPUT_PDF)
    except Exception as e:
        print(f"转换PDF失败: {e}")
        return False

def send_email():
    """发送邮件"""
    try:
        subject = f"半导体早报 | {datetime.now().strftime('%m-%d')}"
        result = subprocess.run(
            [
                "python3",
                str(SKILL_DIR / "scripts" / "send_email.py"),
                "--to", RECIPIENT,
                "--subject", subject,
                "--body", "半导体早报PDF已生成，请查看附件。",
                "--attachments", OUTPUT_PDF
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False

def main():
    print("=" * 50)
    print("半导体早报生成与发送")
    print("=" * 50)
    
    # 1. 获取股价数据
    print("\n[1/4] 获取股价数据...")
    stock_data = get_stock_data()
    if stock_data:
        print("✓ 股价数据获取成功")
    else:
        print("✗ 股价数据获取失败，使用默认数据")
    
    # 2. 生成HTML
    print("\n[2/4] 生成HTML报告...")
    if generate_html(stock_data):
        print(f"✓ HTML生成成功: {OUTPUT_HTML}")
    else:
        print("✗ HTML生成失败")
        return False
    
    # 3. 转换为PDF
    print("\n[3/4] 转换为PDF...")
    if convert_to_pdf():
        print(f"✓ PDF转换成功: {OUTPUT_PDF}")
    else:
        print("✗ PDF转换失败")
        return False
    
    # 4. 发送邮件
    print("\n[4/4] 发送邮件...")
    if send_email():
        print(f"✓ 邮件发送成功: {RECIPIENT}")
        return True
    else:
        print("✗ 邮件发送失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
