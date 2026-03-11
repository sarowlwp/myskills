#!/usr/bin/env python3
"""
PDF转换与邮件发送合并脚本 - 热点简报
接收HTML文件，转换为PDF并发送邮件
支持通过环境变量或自动检测定位相关脚本
"""

import os
import subprocess
import sys
from pathlib import Path

def get_skill_dir():
    """
    自动检测 skill 目录，优先级：
    1. 环境变量 HOTSPOT_SKILL_DIR
    2. 根据本脚本位置推断
    3. 常见路径尝试
    """
    # 优先级1：环境变量
    env_dir = os.environ.get('HOTSPOT_SKILL_DIR')
    if env_dir:
        return Path(env_dir)

    # 优先级2：根据本脚本位置推断（scripts/convert_and_send.py）
    script_dir = Path(__file__).parent.resolve()
    skill_dir = script_dir.parent
    if (skill_dir / "assets" / "template.html").exists():
        return skill_dir

    # 优先级3：尝试常见路径
    try_paths = [
        Path.home() / ".openclaw" / "workspace" / "skills" / "hotspot-briefing",
        Path.home() / ".claude" / "skills" / "hotspot-briefing",
        Path("/usr/local/share/hotspot-briefing"),
        Path("/opt/hotspot-briefing"),
    ]
    for try_path in try_paths:
        if (try_path / "assets" / "template.html").exists():
            return try_path

    raise RuntimeError(
        "无法定位 hotspot-briefing skill 目录。\n"
        "请设置 HOTSPOT_SKILL_DIR 环境变量，或确保脚本位于 skill/scripts/ 目录下。"
    )


def find_node():
    """查找 Node.js 可执行文件"""
    # 环境变量指定
    env_node = os.environ.get('NODE_PATH') or os.environ.get('NODE_BIN')
    if env_node:
        return env_node

    # 尝试系统 PATH
    import shutil
    node_path = shutil.which('node')
    if node_path:
        return node_path

    # 常见安装路径
    common_paths = [
        '/usr/bin/node',
        '/usr/local/bin/node',
        '/opt/homebrew/bin/node',
        str(Path.home() / '.nvm' / 'versions' / 'node' / '*'/ 'bin' / 'node'),
    ]
    for path in common_paths:
        import glob
        matches = glob.glob(path)
        for match in matches:
            if Path(match).exists():
                return match

    raise RuntimeError(
        "未找到 Node.js 可执行文件。\n"
        "请确保 Node.js 已安装并添加到 PATH，或设置 NODE_PATH 环境变量。"
    )


def find_python():
    """查找 Python 可执行文件"""
    # 环境变量指定
    env_python = os.environ.get('PYTHON_PATH') or os.environ.get('PYTHON_BIN')
    if env_python:
        return env_python

    # 当前解释器
    return sys.executable


def convert_and_send(html_path, recipient, subject, body="简报PDF已生成，请查看附件。"):
    """转换HTML为PDF并发送邮件"""

    # 获取必要的路径
    skill_dir = get_skill_dir()
    node_bin = find_node()
    python_bin = find_python()

    # 生成PDF路径
    html_path = Path(html_path).resolve()
    pdf_path = html_path.with_suffix('.pdf')

    # 脚本路径
    html_to_pdf_script = skill_dir / "scripts" / "html_to_pdf.js"
    send_email_script = skill_dir / "scripts" / "send_email.py"

    if not html_to_pdf_script.exists():
        raise FileNotFoundError(f"找不到 PDF 转换脚本: {html_to_pdf_script}")
    if not send_email_script.exists():
        raise FileNotFoundError(f"找不到邮件发送脚本: {send_email_script}")

    print(f"Skill 目录: {skill_dir}")
    print(f"Node 路径: {node_bin}")
    print(f"Python 路径: {python_bin}")

    # 步骤1: 转换PDF
    print(f"\n[1/2] 转换PDF: {html_path} -> {pdf_path}")
    try:
        result = subprocess.run(
            [node_bin, str(html_to_pdf_script), str(html_path), str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(html_path.parent)  # 在HTML所在目录运行
        )
        if result.returncode != 0:
            print(f"PDF转换失败:\n{result.stderr}")
            return False
        if not pdf_path.exists():
            print("PDF文件未生成")
            return False
        print(f"✓ PDF转换成功: {pdf_path}")
    except subprocess.TimeoutExpired:
        print("PDF转换超时（60秒）")
        return False
    except Exception as e:
        print(f"PDF转换异常: {e}")
        return False

    # 步骤2: 发送邮件
    print(f"\n[2/2] 发送邮件到: {recipient}")
    try:
        result = subprocess.run(
            [
                python_bin,
                str(send_email_script),
                "--to", recipient,
                "--subject", subject,
                "--body", body,
                "--attachments", str(pdf_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(f"邮件发送stderr: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("邮件发送超时（60秒）")
        return False
    except Exception as e:
        print(f"发送邮件异常: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("用法: python3 convert_and_send.py <html文件> <收件人邮箱> <邮件主题> [邮件正文]")
        print("示例: python3 convert_and_send.py /tmp/hotspot_briefing.html user@example.com '热点简报 | 03-11 15:30'")
        print("")
        print("环境变量:")
        print("  HOTSPOT_SKILL_DIR    - Skill 根目录（可选，默认自动检测）")
        print("  NODE_PATH            - Node.js 可执行文件路径（可选）")
        print("  PYTHON_PATH          - Python 可执行文件路径（可选）")
        print("  HOTSPOT_SMTP_JSON    - SMTP 配置 JSON 字符串（可选）")
        print("  HOTSPOT_SMTP_CONFIG  - SMTP 配置文件路径（可选）")
        sys.exit(1)

    html_path = sys.argv[1]
    recipient = sys.argv[2]
    subject = sys.argv[3]
    body = sys.argv[4] if len(sys.argv) > 4 else "简报PDF已生成，请查看附件。"

    print("=" * 50)
    print("PDF转换与邮件发送 - 热点简报")
    print("=" * 50)

    try:
        success = convert_and_send(html_path, recipient, subject, body)

        if success:
            print("\n✓ 任务完成: PDF已生成并发送")
            sys.exit(0)
        else:
            print("\n✗ 任务失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
