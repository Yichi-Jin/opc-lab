import csv
import json
import os
from config import Config

def convert_flat():
    if not os.path.exists(Config.METADATA_FILE):
        print(f"❌ 找不到输入文件: {Config.METADATA_FILE}")
        return

    print(f"📂 正在读取 {Config.METADATA_FILE} ...")

    json_data = {}
    count = 0

    with open(Config.METADATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # ... (逻辑保持不变) ...
            pass

    output_file = Config.NODES_CONFIG_FILE 
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 转换完成！配置文件已更新: {output_file}")

if __name__ == "__main__":
    convert_flat()