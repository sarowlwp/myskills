#!/usr/bin/env python3
"""
邮件发送脚本 - 用于热点简报
支持环境变量、命令行参数和配置文件多种配置方式
"""

import argparse
import json
import logging
import os
import smtplib
import sys
import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# 默认配置路径（可通过环境变量覆盖）
DEFAULT_CONFIG_DIR = Path(os.environ.get('HOTSPOT_CONFIG_DIR', Path.home() / ".config" / "hotspot-briefing"))
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "smtp-config.json"
DEFAULT_LOG_DIR = Path(os.environ.get('HOTSPOT_LOG_DIR', Path.home() / ".local" / "log" / "hotspot-briefing"))
DEFAULT_LOG_PATH = DEFAULT_LOG_DIR / "smtp-sender.log"


def get_logger(log_path=None, verbose=False):
    """获取日志记录器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # 清除已有处理器
    logger.handlers = []

    # 格式化
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出（如果指定）
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_config(config_path=None):
    """
    加载SMTP配置，优先级：
    1. 环境变量 HOTSPOT_SMTP_JSON（JSON字符串）
    2. 环境变量 HOTSPOT_SMTP_CONFIG（配置文件路径）
    3. 命令行指定的配置文件
    4. 默认配置文件
    """
    # 优先级1：环境变量 JSON
    env_json = os.environ.get('HOTSPOT_SMTP_JSON')
    if env_json:
        try:
            return json.loads(env_json)
        except json.JSONDecodeError as e:
            print(f"环境变量 HOTSPOT_SMTP_JSON 格式错误: {e}")

    # 优先级2/3/4：配置文件
    config_file = (
        os.environ.get('HOTSPOT_SMTP_CONFIG') or  # 环境变量指定
        config_path or                             # 命令行指定
        DEFAULT_CONFIG_PATH                        # 默认路径
    )

    config_file = Path(config_file)

    if not config_file.exists():
        raise FileNotFoundError(
            f"配置文件不存在: {config_file}\n"
            f"请通过以下方式之一提供配置:\n"
            f"  1. 设置 HOTSPOT_SMTP_JSON 环境变量（JSON字符串）\n"
            f"  2. 设置 HOTSPOT_SMTP_CONFIG 环境变量（配置文件路径）\n"
            f"  3. 使用 --config 参数指定配置文件\n"
            f"  4. 创建默认配置文件: {DEFAULT_CONFIG_PATH}\n\n"
            f"配置格式示例:\n"
            f'{{"server": "smtp.gmail.com", "port": 465, "username": "xxx", "password": "xxx", "emailFrom": "sender@example.com"}}'
        )

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise RuntimeError(f"加载配置失败: {e}")


def send_email(to, subject, body, attachments=None, max_retries=3, config=None, logger=None):
    """发送邮件"""
    if logger is None:
        logger = get_logger()

    if config is None:
        config = load_config()

    # 验证必要配置
    required_keys = ['server', 'port', 'username', 'password']
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(f"配置缺少必要字段: {missing}")

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
            logger.info(f"连接到 SMTP 服务器: {config['server']}:{config['port']}")
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
    parser = argparse.ArgumentParser(description='热点简报邮件发送')
    parser.add_argument('--to', required=True, help='收件人邮箱')
    parser.add_argument('--subject', required=True, help='邮件主题')
    parser.add_argument('--body', default='简报PDF已生成，请查看附件。', help='邮件正文')
    parser.add_argument('--attachments', nargs='+', help='附件路径')
    parser.add_argument('--config', help='配置文件路径（覆盖默认路径）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--log', help='日志文件路径')

    args = parser.parse_args()

    # 设置日志
    log_path = args.log or DEFAULT_LOG_PATH if not os.environ.get('HOTSPOT_NO_LOG') else None
    logger = get_logger(log_path=log_path, verbose=args.verbose)

    try:
        config = load_config(args.config)
        success = send_email(
            to=args.to,
            subject=args.subject,
            body=args.body,
            attachments=args.attachments,
            config=config,
            logger=logger
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"发送失败: {e}")
        print(f"✗ 发送失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
