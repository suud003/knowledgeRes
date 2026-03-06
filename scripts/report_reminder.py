"""报告生成提醒脚本.

通过 Windows 系统通知提醒用户执行日报/周报/月报生成指令。
配合 Windows 任务计划定时运行。

使用方式：
    python scripts/report_reminder.py daily     # 日报提醒
    python scripts/report_reminder.py weekly     # 周报提醒
    python scripts/report_reminder.py monthly    # 月报提醒

安装定时任务（需管理员权限）：
    python scripts/setup_report_tasks.py
"""

import sys
import subprocess
import datetime
from pathlib import Path


# 提醒配置
REMINDERS = {
    "daily": {
        "title": "📝 日报提醒",
        "message": "该写日报啦！请打开 CodeBuddy 执行 /generate_daily 指令生成今日日报。",
        "command": "/generate_daily",
    },
    "weekly": {
        "title": "📊 周报提醒",
        "message": "该写周报啦！请打开 CodeBuddy 执行 /generate_weekly 指令生成本周周报。",
        "command": "/generate_weekly",
    },
    "monthly": {
        "title": "📅 月报提醒",
        "message": "该写月报啦！请打开 CodeBuddy 执行 /generate_monthly 指令生成本月月报。",
        "command": "/generate_monthly",
    },
}


def send_toast_notification(title: str, message: str):
    """通过 PowerShell 发送 Windows Toast 通知."""
    # 转义单引号
    title_escaped = title.replace("'", "''")
    message_escaped = message.replace("'", "''")

    ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast duration="long">
    <visual>
        <binding template="ToastGeneric">
            <text>{title_escaped}</text>
            <text>{message_escaped}</text>
        </binding>
    </visual>
    <audio src="ms-winsoundevent:Notification.Reminder"/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Moos PA").Show($toast)
"""
    try:
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            timeout=10,
        )
        return True
    except Exception:
        return False


def send_msgbox_fallback(title: str, message: str):
    """备用方案：使用 VBScript 弹出消息框."""
    vbs_script = f'MsgBox "{message}", 64, "{title}"'
    try:
        import tempfile
        vbs_path = Path(tempfile.gettempdir()) / "pa_reminder.vbs"
        vbs_path.write_text(vbs_script, encoding="gbk")
        subprocess.Popen(["wscript", str(vbs_path)])
        return True
    except Exception:
        return False


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in REMINDERS:
        print("用法: python report_reminder.py <daily|weekly|monthly>")
        print("  daily   - 日报提醒（每天 23:00）")
        print("  weekly  - 周报提醒（每周日 23:00）")
        print("  monthly - 月报提醒（每月最后一天 23:00）")
        sys.exit(1)

    report_type = sys.argv[1]
    config = REMINDERS[report_type]
    now = datetime.datetime.now()

    print(f"⏰ [{now.strftime('%Y-%m-%d %H:%M:%S')}] 触发 {config['title']}")

    # 发送通知
    if not send_toast_notification(config["title"], config["message"]):
        print("  Toast 通知失败，尝试备用弹窗...")
        if not send_msgbox_fallback(config["title"], config["message"]):
            print("  ❌ 所有通知方式均失败")
            sys.exit(1)

    print(f"  ✅ 已发送提醒: {config['message']}")
    print(f"  💡 请在 CodeBuddy 中执行: {config['command']}")


if __name__ == "__main__":
    main()
