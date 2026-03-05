import asyncio
import psycopg
from config import Config

async def clean_db():
    # 🎯 目标时间：删除这个时间点及之后的所有数据
    # Postgres 会自动根据你的系统时区处理这个字符串
    target_time = "2026-02-05 16:57:00"
    
    print(f"🧹 准备清理数据库...")
    print(f"⚠️  将删除 [ {target_time} ] 及以后的所有 tag_values 记录")
    
    try:
        # 建立连接
        async with await psycopg.AsyncConnection.connect(Config.DB_CONFIG) as conn:
            async with conn.cursor() as cur:
                # 1. 查询一下即将删除多少条（可选，为了心中有数）
                await cur.execute(
                    "SELECT count(*) FROM tag_values WHERE time >= %s", 
                    (target_time,)
                )
                count_before = (await cur.fetchone())[0]
                
                if count_before == 0:
                    print("✅ 没有发现符合条件的数据，无需删除。")
                    return

                print(f"🔍 发现 {count_before} 条目标数据，正在执行删除...")

                # 2. 执行删除
                await cur.execute(
                    "DELETE FROM tag_values WHERE time >= %s", 
                    (target_time,)
                )
                await conn.commit()
                
        print(f"🗑️  成功删除了 {count_before} 条记录")
        print("✅ 数据库已清理完毕")

    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    asyncio.run(clean_db())