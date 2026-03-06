#!/usr/bin/env python3
"""
PDF转换与邮件发送合并脚本
接收HTML文件，转换为PDF并发送邮件
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path("/root/.openclaw/workspace/skills/semiconductor-daily")

def convert_and_send(html_path, recipient, subject, body="报告PDF已生成，请查看附件。"):
    """转换HTML为PDF并发送邮件"""
    
    # 生成PDF路径
    pdf_path = html_path.replace('.html', '.pdf')
    
    # 步骤1: 转换PDF
    print(f"[1/2] 转换PDF: {html_path} -> {pdf_path}")
    try:
        result = subprocess.run(
            ["node", str(SKILL_DIR / "scripts" / "html_to_pdf.js"), html_path, pdf_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/root/.openclaw/workspace"
        )
        if result.returncode != 0:
            print(f"PDF转换失败: {result.stderr}")
            return False
        if not os.path.exists(pdf_path):
            print("PDF文件未生成")
            return False
        print(f"✓ PDF转换成功: {pdf_path}")
    except Exception as e:
        print(f"PDF转换异常: {e}")
        return False
    
    # 步骤2: 发送邮件
    print(f"[2/2] 发送邮件到: {recipient}")
    try:
        result = subprocess.run(
            [
                "python3",
                str(SKILL_DIR / "scripts" / "send_email.py"),
                "--to", recipient,
                "--subject", subject,
                "--body", body,
                "--attachments", pdf_path
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/root/.openclaw/workspace"
        )
        print(result.stdout)
        if result.stderr:
            print(f"邮件发送stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"发送邮件异常: {e}")
        return False

def main():
    if len(sys.argv) < 4:
        print("用法: python3 convert_and_send.py <html文件> <收件人邮箱> <邮件主题> [邮件正文]")
        print("示例: python3 convert_and_send.py /tmp/report.html sarowlwp@gmail.com '半导体早报 | 03-06'")
        sys.exit(1)
    
    html_path = sys.argv[1]
    recipient = sys.argv[2]
    subject = sys.argv[3]
    body = sys.argv[4] if len(sys.argv) > 4 else "报告PDF已生成，请查看附件。"
    
    print("=" * 50)
    print("PDF转换与邮件发送")
    print("=" * 50)
    
    success = convert_and_send(html_path, recipient, subject, body)
    
    if success:
        print("\n✓ 任务完成: PDF已生成并发送")
        sys.exit(0)
    else:
        print("\n✗ 任务失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
