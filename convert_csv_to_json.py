import csv
import json
import os
from config import Config

INPUT_FILE = Config.NODES_LIST_FILE # e.g. "nodes_list.csv"
OUTPUT_FILE = Config.NODES_CONFIG_FILE # e.g. "nodes.json"

def convert():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到输入文件: {INPUT_FILE}")
        print("   请先运行 'uv run python print_nodes.py' 生成 CSV 文件。")
        return

    print(f"📂 正在读取 {INPUT_FILE} ...")

    # 结果字典
    # 结构: { "组名(父节点名)": { "变量名": "NodeID" } }
    json_data = {}
    
    # 用于追踪每一层的父节点名称，key=depth, value=name
    # 默认第 -1 层是 Root
    parents_track = {-1: "Root"}

    with open(INPUT_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        count_vars = 0
        
        for row in reader:
            try:
                depth = int(row["Depth"])
                node_type = row["Type"]
                # 去除 CSV 中为了排版加的缩进空格
                raw_name = row["Name"].strip()
                # 替换空格为下划线，方便作为 Key
                clean_name = raw_name.replace(" ", "_") 
                node_id = row["NodeID"]

                # 逻辑分支
                if "Object" in node_type or "Folder" in node_type:
                    # 如果是文件夹，记录它为当前深度的“父节点”
                    parents_track[depth] = clean_name
                    # 初始化这个组（如果还没存在）
                    if clean_name not in json_data:
                        json_data[clean_name] = {}
                        
                elif "Variable" in node_type:
                    # 如果是变量，找到它的直接父节点（上一层 depth-1）
                    parent_group = parents_track.get(depth - 1, "Root")
                    
                    # 确保父组存在
                    if parent_group not in json_data:
                        json_data[parent_group] = {}
                    
                    # 写入数据
                    json_data[parent_group][clean_name] = node_id
                    count_vars += 1

            except ValueError:
                continue # 跳过标题行或格式错误的行

    # 过滤掉空的组（只有文件夹没有变量的组）
    final_data = {k: v for k, v in json_data.items() if v}

    # 写入 JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 转换完成！")
    print(f"   - 已提取变量数: {count_vars}")
    print(f"   - 有效分组数: {len(final_data)}")
    print(f"   - 文件已保存至: {OUTPUT_FILE}")
    print("⚠️  注意: 原有的 nodes.json 已被覆盖。")

if __name__ == "__main__":
    convert()