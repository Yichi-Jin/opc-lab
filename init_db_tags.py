import asyncio
import csv
import os
import psycopg
from config import Config  # <--- 引入配置
from node_loader import load_nodes

async def init_tags():
    print("🚀 开始初始化数据库标签表...")
    
    # 1. 加载节点配置
    try:
        nodes_config = load_nodes()
    except Exception as e:
        print(f"❌ 无法加载节点配置: {e}")
        return

    # 2. 尝试加载元数据 (从 Config 读取路径)
    metadata_map = {} 
    
    # [修改点] 使用 Config.METADATA_FILE
    if os.path.exists(Config.METADATA_FILE):
        print(f"📖 发现元数据文件: {Config.METADATA_FILE}，正在读取描述信息...")
        try:
            with open(Config.METADATA_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    g = row.get('Group', '').strip()
                    n = row.get('Name', '').strip()
                    if g and n:
                        key = f"{g}.{n}" if g != n else n
                        metadata_map[key] = (row.get('Description', ''), row.get('Unit', ''))
        except Exception as e:
            print(f"⚠️ 读取元数据文件出错: {e}")
    else:
        print(f"⚠️ 未找到 {Config.METADATA_FILE}，标签描述将为空。")

    # 3. 准备写入数据库
    # 提取连接字符串中的参数 (去除 psycopg_pool 可能不支持的参数 if any)
    conn_str = Config.DB_CONFIG
    
    inserted_count = 0
    updated_count = 0

    try:
        async with await psycopg.AsyncConnection.connect(conn_str) as conn:
            async with conn.cursor() as cur:
                for group, items in nodes_config.items():
                    for name, _ in items.items():
                        # 生成 Tag Key (必须与 scheduler.py 逻辑完全一致)
                        tag_name = f"{group}.{name}" if group != name else name
                        
                        # 获取元数据
                        desc, unit = metadata_map.get(tag_name, (None, None))
                        
                        # 执行插入或更新 (Upsert)
                        # 如果标签已存在，则更新描述和单位
                        await cur.execute("""
                            INSERT INTO tags (tag_name, description, unit)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (tag_name) 
                            DO UPDATE SET 
                                description = COALESCE(EXCLUDED.description, tags.description),
                                unit = COALESCE(EXCLUDED.unit, tags.unit)
                        """, (tag_name, desc, unit))
                        
                        if cur.rowcount > 0:
                            # 简单的计数逻辑 (Postgres merge 返回值比较复杂，这里简化处理)
                            inserted_count += 1
                
                await conn.commit()
                
        print(f"✅ 数据库初始化完成！")
        print(f"   已处理 {inserted_count} 个位号。")
        print("   现在可以运行 scheduler.py 了。")

    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")

if __name__ == "__main__":
    asyncio.run(init_tags())