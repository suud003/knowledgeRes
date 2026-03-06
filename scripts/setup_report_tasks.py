"""定时任务安装脚本.

一键创建 Windows 任务计划，自动设置日报/周报/月报的定时提醒。

规则：
    - 每晚 23:00 执行日报提醒
    - 每周日 23:00 执行周报提醒
    - 每月最后一天 23:00 执行月报提醒

使用方式（需管理员权限）：
    python scripts/setup_report_tasks.py          # 安装所有定时任务
    python scripts/setup_report_tasks.py --remove  # 移除所有定时任务
    python scripts/setup_report_tasks.py --status  # 查看任务状态
"""

import sys
import subprocess
from pathlib import Path


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
REMINDER_SCRIPT = PROJECT_ROOT / "scripts" / "report_reminder.py"
PYTHON_EXE = sys.executable  # 当前 Python 解释器路径

# 任务名称前缀
TASK_PREFIX = "MoosPA"

# 任务配置
TASKS = {
    "daily": {
        "name": f"{TASK_PREFIX}_DailyReport",
        "description": "Moos PA - 每日日报提醒（23:00）",
        "schedule": "/sc daily /st 23:00",
    },
    "weekly": {
        "name": f"{TASK_PREFIX}_WeeklyReport",
        "description": "Moos PA - 每周日周报提醒（23:00）",
        "schedule": "/sc weekly /d SUN /st 23:00",
    },
    "monthly": {
        "name": f"{TASK_PREFIX}_MonthlyReport",
        "description": "Moos PA - 每月末月报提醒（23:00）",
        # Windows 任务计划不直接支持"每月最后一天"，使用每月执行 + 脚本内部判断
        "schedule": "/sc monthly /d LASTDAY /st 23:00",
    },
}


def run_schtasks(args: str, check: bool = True) -> subprocess.CompletedProcess:
    """执行 schtasks 命令."""
    cmd = f"schtasks {args}"
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, encoding="gbk"
    )
    if check and result.returncode != 0:
        # 某些错误是可以忽略的（比如任务不存在时删除）
        pass
    return result


def install_tasks():
    """安装所有定时任务."""
    print("🔧 开始安装定时任务...")
    print(f"  Python: {PYTHON_EXE}")
    print(f"  脚本:   {REMINDER_SCRIPT}")
    print()

    for task_type, config in TASKS.items():
        task_name = config["name"]
        description = config["description"]
        schedule = config["schedule"]

        # 构建执行命令
        cmd = f'"{PYTHON_EXE}" "{REMINDER_SCRIPT}" {task_type}'

        # 先删除旧任务（如果存在）
        run_schtasks(f'/delete /tn "{task_name}" /f', check=False)

        # 创建新任务
        create_cmd = (
            f'/create /tn "{task_name}" '
            f'/tr "{cmd}" '
            f'{schedule} '
            f'/f'
        )

        result = run_schtasks(create_cmd)

        if result.returncode == 0:
            print(f"  ✅ {description} - 已创建")
        else:
            print(f"  ❌ {description} - 创建失败")
            if result.stderr:
                print(f"     错误: {result.stderr.strip()}")
            if "请求的操作需要提升" in (result.stderr or "") or "Access" in (result.stderr or ""):
                print("     💡 提示: 请以管理员身份运行此脚本")

    print()
    print("✅ 定时任务安装完成！")
    print()
    print("📋 任务计划：")
    print("  • 每天 23:00 → 日报提醒 → 执行 /generate_daily")
    print("  • 每周日 23:00 → 周报提醒 → 执行 /generate_weekly")
    print("  • 每月末 23:00 → 月报提醒 → 执行 /generate_monthly")


def remove_tasks():
    """移除所有定时任务."""
    print("🗑️ 移除定时任务...")

    for task_type, config in TASKS.items():
        task_name = config["name"]
        result = run_schtasks(f'/delete /tn "{task_name}" /f')

        if result.returncode == 0:
            print(f"  ✅ {task_name} - 已移除")
        else:
            print(f"  ⚠️ {task_name} - 未找到或移除失败")

    print("\n✅ 所有定时任务已移除")


def show_status():
    """查看任务状态."""
    print("📊 定时任务状态：")
    print()

    for task_type, config in TASKS.items():
        task_name = config["name"]
        result = run_schtasks(f'/query /tn "{task_name}" /fo LIST /v', check=False)

        if result.returncode == 0 and result.stdout:
            print(f"  📌 {config['description']}")
            # 提取关键信息
            for line in result.stdout.split("\n"):
                line = line.strip()
                if any(
                    key in line
                    for key in ["状态", "Status", "下次运行时间", "Next Run", "上次运行时间", "Last Run"]
                ):
                    print(f"     {line}")
            print()
        else:
            print(f"  ⚪ {config['description']} - 未安装")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--remove":
            remove_tasks()
            return
        elif sys.argv[1] == "--status":
            show_status()
            return
        elif sys.argv[1] == "--help":
            print(__doc__)
            return

    install_tasks()


if __name__ == "__main__":
    main()
