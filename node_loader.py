# node_loader.py
import json
import os
from config import Config

# 定义配置文件路径
JSON_FILE_PATH = Config.NODES_CONFIG_FILE # e.g. "nodes.json"

def load_nodes():
    """读取并返回完整的节点配置字典"""
    if not os.path.exists(JSON_FILE_PATH):
        raise FileNotFoundError(f"❌ 找不到配置文件: {JSON_FILE_PATH}")
    
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise Exception(f"❌ JSON 格式错误: {e}")

def get_node_id(group, name):
    """
    辅助函数：快速获取特定节点ID
    用法: get_node_id("production_line_1", "temperature")
    """
    data = load_nodes()
    
    # 检查组是否存在
    if group not in data:
        raise KeyError(f"❌ 找不到组 '{group}'")
        
    # 检查节点名称是否存在
    if name not in data[group]:
        raise KeyError(f"❌ 在 '{group}' 中找不到节点 '{name}'")
        
    return data[group][name]

# 用于简单测试
if __name__ == "__main__":
    try:
        # 测试读取
        tid = get_node_id("test_environment", "simulation_value")
        print(f"✅ 读取成功: {tid}")
    except Exception as e:
        print(e)