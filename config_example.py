class Config:
    # === OPC UA 服务器配置 ===
    URL = "opc.tcp://127.0.0.1:4840"  # 替换为实际的内网 IP
    DB_CONFIG = "dbname=opc_lab_data user=your_user password=your_password host=localhost"
    # === 数据库配置 ===
    # 建议生产环境从环境变量读取: os.getenv("DB_PASSWORD")
    DB_CONFIG = "dbname=opc_lab_data user=your_user password=your_password host=localhost"
    # === 采集策略 ===
    COLLECT_INTERVAL = 10.0
    # === 文件路径配置 ===
    # 全量位号列表文件 (从 OPC UA 扫描生成的 CSV 文件)
    NODES_LIST_FILE = "nodes_list.csv"
    # 节点配置文件 (中间件)
    NODES_CONFIG_FILE = "nodes.json"
    # 位号元数据文件 (整理得到的关注列表)
    METADATA_FILE = "tracked_tags_values.csv"