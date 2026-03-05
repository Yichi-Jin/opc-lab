# client_manager.py
from asyncua import Client
from config import Config
import logging

# 设置日志，方便调试
logging.basicConfig(level=logging.WARNING)

class OpcClient:
    def __init__(self):
        self.url = Config.URL
        self.client = Client(url=self.url)

    async def __aenter__(self):
        """支持 'async with' 语法"""
        await self.client.connect()
        # print(f"✅ 已连接至服务器: {self.url}")
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出时自动断开连接"""
        await self.client.disconnect()
        # print("❎ 连接已关闭")