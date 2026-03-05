import asyncio
import datetime
import signal
from client_manager import OpcClient
from node_loader import load_nodes
from db_manager import DbManager
from config import Config

shutdown_event = asyncio.Event()

def handle_signal():
    """捕获 Ctrl+C 信号"""
    print("\n🛑 正在停止服务...")
    shutdown_event.set()

async def collection_job(client, nodes_config):
    """单次采集任务"""
    # 记录本次采集统一的时间点
    # [修改点] 统一使用“采集时间”作为入库时间，确保唯一且递增
    start_time = datetime.datetime.now(datetime.timezone.utc)
    collect_time = datetime.datetime.now(datetime.timezone.utc)
    
    batch_data = []
    
    for group_name, nodes in nodes_config.items():
        for name, node_id in nodes.items():
            tag_key = f"{group_name}.{name}" if group_name != name else name
            
            try:
                node = client.get_node(node_id)
                dv = await node.read_data_value()
                
                val = str(dv.Value.Value)
                status = dv.StatusCode.name
                ts = collect_time # ts = dv.SourceTimestamp or ... (弃用)

                batch_data.append((ts, tag_key, val, status))
                
            except Exception:
                pass
    
    # 写入数据库
    if batch_data:
        try:
            await DbManager.insert_batch(batch_data)
            duration = (datetime.datetime.now() - start_time).total_seconds()
            print(f"✅ [{start_time.strftime('%H:%M:%S')}] 已存储 {len(batch_data)} 条数据 (耗时 {duration:.2f}s)")
        except Exception as e:
            print(f"❌ 数据库写入失败: {e}")

async def main():
    # 注册信号处理
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, handle_signal)
    loop.add_signal_handler(signal.SIGTERM, handle_signal)

    print(f"🚀 启动周期采集服务 (周期: {Config.COLLECT_INTERVAL}s)")
    
    # 1. 初始化资源
    try:
        nodes_config = load_nodes()
        await DbManager.initialize()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    # 2. 建立长连接
    # 注意：这里我们把 OpcClient 的生命周期拉长到整个程序运行期间
    async with OpcClient() as client:
        print("🔗 OPC UA 连接已建立，开始轮询...")
        
        # 3. 循环采集
        while not shutdown_event.is_set():
            loop_start = asyncio.get_running_loop().time()
            
            # 执行采集
            await collection_job(client, nodes_config)
            
            # 计算剩余休眠时间，确保周期准确
            elapsed = asyncio.get_running_loop().time() - loop_start
            sleep_time = max(0, Config.COLLECT_INTERVAL - elapsed)
            
            if sleep_time == 0:
                print("⚠️ 警告: 采集耗时超过周期，可能需要优化或延长周期")
            
            # 智能休眠 (响应中断信号)
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=sleep_time)
            except asyncio.TimeoutError:
                continue # 超时意味着没收到停止信号，继续下一轮

    # 4. 清理资源
    await DbManager.close()
    print("👋 服务已安全关闭")

if __name__ == "__main__":
    asyncio.run(main())