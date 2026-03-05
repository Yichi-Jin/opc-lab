import asyncio
import csv
import datetime
import os
from client_manager import OpcClient
from node_loader import load_nodes

# 定义报告保存的文件夹
REPORT_DIR = "reports"

# === 筛选开关 ===
# True: 只记录 Status 为 "Good" 的数据
# False: 记录所有数据（包括 Error/Bad）
FILTER_GOOD_ONLY = False
# =================

async def generate_report():
    # 1. 准备工作
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 为了区分文件，可以在文件名里加个标记
    suffix = "_filtered" if FILTER_GOOD_ONLY else "_all"
    filename = f"{REPORT_DIR}/report_{timestamp_str}{suffix}.csv"
    
    try:
        nodes_config = load_nodes()
    except Exception as e:
        print(f"❌ 无法加载节点配置: {e}")
        return

    print(f"🚀 开始采集数据 (筛选模式: {'只看 Good' if FILTER_GOOD_ONLY else '全部记录'})...")

    # 2. 连接并采集
    async with OpcClient() as client:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Group", "Name", "NodeID", "Value", "Status", "Timestamp"])
            
            # 计数器
            count_total = 0
            count_saved = 0
            
            for group_name, nodes in nodes_config.items():
                # 仅为了进度条显示美观，不刷屏
                print(f"\r⏳ 正在处理组: {group_name:<20}", end="", flush=True)
                
                for name, node_id in nodes.items():
                    count_total += 1
                    value = "N/A"
                    status = "Error"
                    time_read = datetime.datetime.now().isoformat()
                    
                    try:
                        node = client.get_node(node_id)
                        dv = await node.read_data_value()
                        
                        value = dv.Value.Value
                        status = dv.StatusCode.name
                        if dv.SourceTimestamp:
                            time_read = dv.SourceTimestamp.isoformat()
                            
                    except Exception as e:
                        value = f"Error: {str(e)}"
                        status = "ReadFailed"
                    
                    # === 核心筛选逻辑 ===
                    if FILTER_GOOD_ONLY:
                        # 只要状态里不包含 "Good"，就跳过不写
                        if "Good" not in status:
                            continue

                    # 写入数据
                    writer.writerow([group_name, name, node_id, value, status, time_read])
                    count_saved += 1
                    
    print(f"\n\n✅ 采集完成！")
    print(f"   - 扫描总节点: {count_total}")
    print(f"   - 实际记录数: {count_saved}")
    print(f"   - 报告文件: {filename}")

if __name__ == "__main__":
    asyncio.run(generate_report())