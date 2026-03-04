"""每日资讯采集脚本.

可配合 Windows 任务计划或 cron 定时运行。
运行后会在 data/raw/rss/ 目录下缓存抓取结果，
下次与 AI 对话时调用 fetch_daily_digest 即可查看。

使用方式：
    python scripts/run_daily_digest.py

配合 Windows 任务计划定时执行：
    schtasks /create /tn "PA_DailyDigest" /tr "python <项目路径>/scripts/run_daily_digest.py" /sc daily /st 09:00
"""

import asyncio
import sys
from pathlib import Path

# 确保可以导入 pa 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 设置工作目录为项目根
import os
os.chdir(project_root)


async def main():
    from pa.scheduler import DailyDigestScheduler

    print("🚀 开始每日资讯预抓取...")
    print(f"📂 项目目录: {project_root}")

    scheduler = DailyDigestScheduler()
    result = await scheduler.fetch_articles()

    print(f"\n📊 抓取结果:")
    print(f"  检查源数: {result['sources_checked']}")
    print(f"  新文章数: {result['total_found']}")

    if result["errors"]:
        print(f"\n⚠️ 错误:")
        for err in result["errors"]:
            print(f"  - {err}")

    if result["articles"]:
        print(f"\n📰 文章列表:")
        for i, article in enumerate(result["articles"], 1):
            title = article.get("title", "无标题")
            source = article.get("source_name", "?")
            print(f"  {i}. [{source}] {title}")

    print(f"\n✅ 预抓取完成！下次与 AI 对话时调用 fetch_daily_digest 即可查看并筛选。")


if __name__ == "__main__":
    asyncio.run(main())
