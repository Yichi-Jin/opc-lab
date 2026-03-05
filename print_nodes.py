import asyncio
import csv
from asyncua import ua
from client_manager import OpcClient

# 定义 CSV 文件名
OUTPUT_FILE = "nodes_list.csv"

async def browse_recursive(node, csv_writer, depth=0, max_depth=3):
    """
    递归遍历并将结果写入 CSV
    """
    if depth > max_depth:
        return

    try:
        children = await node.get_children()
        
        for child in children:
            # 读取属性
            browse_name = await child.read_browse_name()
            node_class = await child.read_node_class()
            node_id = child.nodeid.to_string()
            
            # 转换类型枚举为可读字符串
            type_str = "Folder/Object" if node_class == ua.NodeClass.Object else "Variable"
            
            # 写入一行数据：[层级深度, 类型, 名称, NodeID]
            # 用缩进在名称前表现层级
            indent_name = ("  " * depth) + browse_name.Name
            
            # 写入 CSV
            csv_writer.writerow([depth, type_str, indent_name, node_id])
            
            # 终端打印一个简短的进度点，避免刷屏
            print(".", end="", flush=True)

            # 如果是文件夹，继续递归
            if node_class == ua.NodeClass.Object:
                await browse_recursive(child, csv_writer, depth + 1, max_depth)
                
    except Exception as e:
        print(f"\n❌ 读取错误: {e}")

async def main():
    async with OpcClient() as client:
        print(f"--- 开始扫描，结果将保存至 {OUTPUT_FILE} ---")
        
        # 打开 CSV 文件准备写入
        with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(["Depth", "Type", "Name", "NodeID"])
            
            objects_node = client.get_objects_node()
            await browse_recursive(objects_node, writer)
            
        print(f"\n✅ 扫描完成！请查看 {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())