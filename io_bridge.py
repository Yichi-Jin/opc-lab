import asyncio
import json
import os
import time
from asyncua import Client, ua
from control_config import ControlConfig

async def io_loop():
    print(f"🌉 启动 IO 桥接器 (周期: {ControlConfig.LOOP_RATE}s)...")
    
    # 初始化命令文件 (如果不存在)
    if not os.path.exists(ControlConfig.COMMAND_FILE):
        with open(ControlConfig.COMMAND_FILE, 'w') as f:
            json.dump({}, f)

    async with Client(url=ControlConfig.URL) as client:
        print("🔗 OPC UA 连接成功！")
        
        # 预先获取 Node 对象，避免循环中重复查询
        nodes_map = {}
        for alias, node_id in ControlConfig.TAGS.items():
            nodes_map[alias] = client.get_node(node_id)
        
        # 上一次写入的值 (用于去重)
        last_written_values = {}

        while True:
            cycle_start = time.time()
            
            # ===========================
            # 1. READ: 从 OPC 读取当前状态
            # ===========================
            current_state = {}
            for alias, node in nodes_map.items():
                try:
                    # 读取数值
                    val = await node.read_value()
                    current_state[alias] = val
                except Exception as e:
                    current_state[alias] = None
                    print(f"⚠️ 读取失败 {alias}: {e}")
            
            # 加上时间戳
            current_state["_timestamp"] = time.time()
            
            # 写入 state.json (原子写入: 先写临时文件再重命名，防止读到半截数据)
            temp_file = ControlConfig.STATE_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(current_state, f, indent=2)
            os.replace(temp_file, ControlConfig.STATE_FILE)
            
            # ===========================
            # 2. WRITE: 检查并执行写入命令
            # ===========================
            try:
                if os.path.exists(ControlConfig.COMMAND_FILE):
                    with open(ControlConfig.COMMAND_FILE, 'r') as f:
                        commands = json.load(f)
                    
                    # 遍历命令文件里的指令
                    for alias, target_value in commands.items():
                        # 只处理我们定义了的点位
                        if alias in nodes_map and target_value is not None:
                            
                            # 获取当前 OPC 里的实际值 (刚刚读到的)
                            current_val = current_state.get(alias)
                            
                            # 🎯 核心逻辑：防抖动写入
                            # 只有当 (目标值 != 当前值) 且 (我们还没写过这个值) 时才写入
                            # 注意：浮点数比较通常需要一个极小的误差范围，这里简化处理
                            if current_val != target_value and last_written_values.get(alias) != target_value:
                                
                                print(f"📝 [写入] {alias} -> {target_value}")
                                
                                node = nodes_map[alias]
                                # 根据数据类型写入，通常 float
                                await node.write_value(float(target_value), ua.VariantType.Float)
                                
                                # 更新记录
                                last_written_values[alias] = target_value
                            
            except json.JSONDecodeError:
                pass # 文件可能正在被写入，跳过本次
            except Exception as e:
                print(f"❌ 写入过程出错: {e}")

            # ===========================
            # 3. 休眠保持频率
            # ===========================
            elapsed = time.time() - cycle_start
            sleep_time = max(0, ControlConfig.LOOP_RATE - elapsed)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    try:
        asyncio.run(io_loop())
    except KeyboardInterrupt:
        print("\n🛑 IO 桥接器已停止")