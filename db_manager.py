# db_manager.py
from psycopg_pool import AsyncConnectionPool
from config import Config  # <--- 引入配置

class DbManager:
    _pool = None

    @classmethod
    async def initialize(cls):
        """初始化连接池"""
        if cls._pool is None:
            # 使用 Config 中的配置字符串
            print(f"🔌 正在连接数据库: {Config.DB_CONFIG.split('password')[0]}...") # 打印时不显示密码
            cls._pool = AsyncConnectionPool(Config.DB_CONFIG, open=False)
            await cls._pool.open()
            print("📦 数据库连接池已启动")

    @classmethod
    async def close(cls):
        """关闭连接池"""
        if cls._pool:
            await cls._pool.close()
            print("📦 数据库连接池已关闭")

    @classmethod
    async def insert_batch(cls, data_list):
        """
        批量写入数据
        :param data_list: list of tuples [(time, tag_name, value, status), ...]
        """
        if not cls._pool:
            await cls.initialize()

        async with cls._pool.connection() as conn:
            async with conn.cursor() as cur:
                # 使用 COPY 协议进行高速写入
                async with cur.copy("COPY tag_values (time, tag_name, value, status) FROM STDIN") as copy:
                    for row in data_list:
                        await copy.write_row(row)