# 根据 xlsx 点位描述文件生成 nodes_from_tags.json 文件（弃用，请使用 convert_csv_to_json.py 更新实时点位）
import pandas as pd
import json
import os
import glob

# 输出文件名
OUTPUT_FILE = "nodes_from_tags.json"

# 定义文件路径模式 (匹配你的文件名)
# 假设这些 CSV 文件都在当前目录下，或者在一个 tags 文件夹里
# 你可以把 *.csv 改为具体的文件名列表
CSV_FILES_PATTERN = "tags.xlsx"

def generate_config():
    # 查找所有匹配的 CSV 文件
    files = glob.glob(CSV_FILES_PATTERN)
    
    if not files:
        print(f"❌ 未找到匹配的 CSV 文件: {CSV_FILES_PATTERN}")
        return

    print(f"📂 找到 {len(files)} 个位号文件，开始处理...")

    # 结果字典
    nodes_config = {}

    total_tags = 0

    for file_path in files:
        try:
            # 提取文件名作为“大类” (例如 "模拟量输入 (AI)")
            # 去掉前缀和后缀，只保留核心描述
            base_name = os.path.basename(file_path)
            category_name = base_name.split("-")[-1].replace(".csv", "").strip()
            
            # 使用 pandas 读取
            df = pd.read_csv(file_path)
            
            # 寻找包含 "Tag" 或 "位号" 的列
            tag_col = next((c for c in df.columns if "位号" in c or "Tag" in c), None)
            
            if not tag_col:
                print(f"⚠️  跳过 {base_name}: 找不到位号列")
                continue

            # 初始化该类别的字典
            if category_name not in nodes_config:
                nodes_config[category_name] = {}

            # 遍历每一行
            for _, row in df.iterrows():
                tag_name = str(row[tag_col]).strip()
                if not tag_name or tag_name.lower() == 'nan':
                    continue

                # --- 关键：NodeID 生成规则 ---
                # 根据之前的 report，NodeID 格式通常是 "ns=1;s=TAGNAME.VALUE" 或 "ns=1;s=TAGNAME"
                # 这里我们默认生成指向 .VALUE 的 ID，这是最常用的过程值
                # 你可以根据实际情况修改这个后缀
                
                # 规则 A: 针对 PID 回路或复杂对象，通常读 VALUE
                node_id = f"ns=1;s={tag_name}.VALUE"
                
                # 规则 B: 如果是简单的 IO 点，可能不需要 .VALUE (视服务器而定)
                # node_id = f"ns=1;s={tag_name}" 

                # 存入配置： Key=位号名, Value=NodeID
                nodes_config[category_name][tag_name] = node_id
                total_tags += 1
                
        except Exception as e:
            print(f"❌ 处理文件 {file_path} 出错: {e}")

    # 保存为 JSON
    if nodes_config:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(nodes_config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 转换成功！")
        print(f"   - 总计提取位号: {total_tags}")
        print(f"   - 生成文件: {OUTPUT_FILE}")
        print(f"   - 下一步: 请将 main.py 或 node_loader.py 的读取路径改为此文件。")
    else:
        print("⚠️  未提取到任何有效位号。")

if __name__ == "__main__":
    generate_config()