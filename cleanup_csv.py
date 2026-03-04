"""一次性清理脚本 - 删除残留的临时 CSV 文件，运行后自动删除本脚本"""
import pathlib

raw_data_dir = pathlib.Path(r"g:\tianyishao\Moos-share\raw data")
deleted = 0

# 清理 raw data 下所有 440API 相关的 CSV 文件
for csv_file in raw_data_dir.glob("440API拆解_*.csv"):
    try:
        csv_file.unlink()
        print(f"✅ 已删除: {csv_file.name}")
        deleted += 1
    except Exception as e:
        print(f"❌ 删除失败: {csv_file.name} - {e}")

print(f"\n🧹 共清理 {deleted} 个临时 CSV 文件")

# 自删除本脚本
try:
    pathlib.Path(__file__).unlink()
    print("🗑️ 清理脚本已自动删除")
except Exception:
    pass
