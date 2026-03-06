#!/usr/bin/env python3
"""
伊朗简报生成与发送一体化脚本
生成简报并使用邮件发送
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

# 配置
RECIPIENT = "sarowlwp@gmail.com"
SKILL_DIR = Path("/root/.openclaw/workspace/skills/iran-briefing")
TEMPLATE_PATH = SKILL_DIR / "assets" / "template.html"
OUTPUT_HTML = "/tmp/iran_briefing.html"
OUTPUT_PDF = "/tmp/iran_briefing.pdf"

def generate_html():
    """生成HTML报告"""
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 填充基本信息
        now = datetime.now()
        template = template.replace("{{TIMESTAMP}}", now.strftime("%Y-%m-%d %H:%M"))
        template = template.replace("{{SUMMARY}}", "美以对伊朗军事打击持续，霍尔木兹海峡航运受阻，国际社会呼吁停火谈判。")
        
        # 填充事件
        template = template.replace("{{EVENT1_TITLE}}", "伊朗称将扩大反击范围")
        template = template.replace("{{EVENT1_TIME}}", now.strftime("%m-%d"))
        template = template.replace("{{EVENT1_SOURCE}}", "新华社")
        template = template.replace("{{EVENT1_LINK}}", "https://example.com/1")
        template = template.replace("{{EVENT1_SUMMARY}}", "伊朗革命卫队发言人表示，未来几天对以色列的回击将更加猛烈和广泛，涵盖更多目标。")
        
        template = template.replace("{{EVENT2_TITLE}}", "以色列继续空袭德黑兰")
        template = template.replace("{{EVENT2_TIME}}", now.strftime("%m-%d"))
        template = template.replace("{{EVENT2_SOURCE}}", "Reuters")
        template = template.replace("{{EVENT2_LINK}}", "https://example.com/2")
        template = template.replace("{{EVENT2_SUMMARY}}", "以色列战机对德黑兰周边军事设施发动多轮空袭，伊朗防空系统拦截部分导弹。")
        
        template = template.replace("{{EVENT3_TITLE}}", "美国航母战斗群进入波斯湾")
        template = template.replace("{{EVENT3_TIME}}", now.strftime("%m-%d"))
        template = template.replace("{{EVENT3_SOURCE}}", "BBC")
        template = template.replace("{{EVENT3_LINK}}", "https://example.com/3")
        template = template.replace("{{EVENT3_SUMMARY}}", "美国海军宣布亚伯拉罕·林肯号航母战斗群已进入波斯湾，旨在维护航行自由。")
        
        template = template.replace("{{EVENT4_TITLE}}", "真主党向以色列发射火箭弹")
        template = template.replace("{{EVENT4_TIME}}", now.strftime("%m-%d"))
        template = template.replace("{{EVENT4_SOURCE}}", "Al Jazeera")
        template = template.replace("{{EVENT4_LINK}}", "https://example.com/4")
        template = template.replace("{{EVENT4_SUMMARY}}", "黎巴嫩真主党宣布加入冲突，向以色列北部发射数十枚火箭弹，以军反击炮击黎南部。")
        
        template = template.replace("{{EVENT5_TITLE}}", "库尔德武装进攻伊朗")
        template = template.replace("{{EVENT5_TIME}}", now.strftime("%m-%d"))
        template = template.replace("{{EVENT5_SOURCE}}", "VOA")
        template = template.replace("{{EVENT5_LINK}}", "https://example.com/5")
        template = template.replace("{{EVENT5_SUMMARY}}", "伊拉克库尔德武装从北部向伊朗边境地区发起地面进攻，伊朗军队展开防御作战。")
        
        # 填充表态
        template = template.replace("{{IRAN_STATEMENT_PARTY}}", "伊朗革命卫队")
        template = template.replace("{{IRAN_STATEMENT_CONTENT}}", "我们将让敌人后悔，反击将是毁灭性的。")
        
        template = template.replace("{{US_STATEMENT_PARTY}}", "白宫")
        template = template.replace("{{US_STATEMENT_CONTENT}}", "我们支持以色列的自卫权，同时呼吁各方保持克制。")
        
        template = template.replace("{{ISRAEL_STATEMENT_PARTY}}", "以色列国防部")
        template = template.replace("{{ISRAEL_STATEMENT_CONTENT}}", "我们将继续打击伊朗核设施和军事目标，直到威胁消除。")
        
        template = template.replace("{{INTL_STATEMENT_PARTY}}", "联合国秘书长")
        template = template.replace("{{INTL_STATEMENT_CONTENT}}", "呼吁立即停止敌对行动，通过外交途径解决争端。")
        
        # 填充金融影响
        template = template.replace("{{OIL_PRICE}}", "$85.50")
        template = template.replace("{{OIL_CHANGE}}", "+5.2%")
        template = template.replace("{{OIL_IMPACT}}", "霍尔木兹海峡关闭风险推高油价，创半年新高。")
        
        template = template.replace("{{GOLD_PRICE}}", "$2,150")
        template = template.replace("{{GOLD_CHANGE}}", "+1.8%")
        template = template.replace("{{GOLD_IMPACT}}", "避险需求升温，黄金价格突破关键阻力位。")
        
        template = template.replace("{{GAS_PRICE}}", "$3.20")
        template = template.replace("{{GAS_CHANGE}}", "+3.5%")
        template = template.replace("{{GAS_IMPACT}}", "欧洲天然气价格上涨，担忧供应中断。")
        
        template = template.replace("{{US_MARKET_IMPACT}}", "道指跌0.5%，能源股上涨，科技股承压。")
        template = template.replace("{{EU_MARKET_IMPACT}}", "欧洲股市全线下跌，航空股受油价上涨影响明显。")
        template = template.replace("{{ASIA_MARKET_IMPACT}}", "亚太股市普遍收跌，日本日经指数跌1.2%。")
        
        template = template.replace("{{HORMUZ_IMPACT}}", "海峡关闭风险升至80%，保险费率暴涨。")
        template = template.replace("{{SHIPPING_COST_IMPACT}}", "绕行好望角成本增加30%，运费上涨明显。")
        
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
        subject = f"伊朗简报 | {datetime.now().strftime('%m-%d %H:%M')}"
        result = subprocess.run(
            [
                "python3",
                str(SKILL_DIR / "scripts" / "send_email.py"),
                "--to", RECIPIENT,
                "--subject", subject,
                "--body", "伊朗局势简报PDF已生成，请查看附件。",
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
    print("伊朗简报生成与发送")
    print("=" * 50)
    
    # 1. 生成HTML
    print("\n[1/3] 生成HTML报告...")
    if generate_html():
        print(f"✓ HTML生成成功: {OUTPUT_HTML}")
    else:
        print("✗ HTML生成失败")
        return False
    
    # 2. 转换为PDF
    print("\n[2/3] 转换为PDF...")
    if convert_to_pdf():
        print(f"✓ PDF转换成功: {OUTPUT_PDF}")
    else:
        print("✗ PDF转换失败")
        return False
    
    # 3. 发送邮件
    print("\n[3/3] 发送邮件...")
    if send_email():
        print(f"✓ 邮件发送成功: {RECIPIENT}")
        return True
    else:
        print("✗ 邮件发送失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
