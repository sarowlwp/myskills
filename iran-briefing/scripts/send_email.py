#!/usr/bin/env python3
"""
邮件发送脚本 - 用于伊朗简报
"""

import argparse
import json
import logging
import smtplib
import sys
import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# 配置路径
CONFIG_PATH = Path.home() / ".openclaw" / "smtp-config.json"
LOG_PATH = Path.home() / ".openclaw" / "smtp-sender.log"

# 日志设置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """加载SMTP配置"""
    if not CONFIG_PATH.exists():
        logger.error(f"配置文件不存在: {CONFIG_PATH}")
        sys.exit(1)
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        sys.exit(1)


def send_email(to, subject, body, attachments=None, max_retries=3):
    """发送邮件"""
    config = load_config()
    
    msg = MIMEMultipart()
    msg['From'] = config.get('emailFrom', config['username'])
    msg['To'] = to
    msg['Subject'] = subject
    
    # 添加邮件正文
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加附件
    if attachments:
        for filepath in attachments:
            try:
                with open(filepath, 'rb') as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=Path(filepath).name
                    )
                    msg.attach(attachment)
                    logger.info(f"已添加附件: {filepath}")
            except Exception as e:
                logger.error(f"添加附件失败 {filepath}: {e}")
    
    # 重试发送
    for attempt in range(1, max_retries + 1):
        try:
            server = smtplib.SMTP_SSL(config['server'], config['port'])
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功: {to}")
            print(f"✓ 邮件已发送至 {to}")
            return True
            
        except Exception as e:
            logger.error(f"尝试 {attempt}/{max_retries} 失败: {e}")
            if attempt == max_retries:
                logger.error("所有重试失败")
                return False
    
    return False


def main():
    parser = argparse.ArgumentParser(description='伊朗简报邮件发送')
    parser.add_argument('--to', required=True, help='收件人邮箱')
    parser.add_argument('--subject', required=True, help='邮件主题')
    parser.add_argument('--body', default='简报PDF已生成，请查看附件。', help='邮件正文')
    parser.add_argument('--attachments', nargs='+', help='附件路径')
    
    args = parser.parse_args()
    
    success = send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        attachments=args.attachments
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
