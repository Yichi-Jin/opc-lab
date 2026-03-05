# 🏭 Industrial OPC UA Data Pipeline

这是一个专为 macOS/Linux 环境设计的工业物联网 (IIoT) 数据采集系统。它能够连接 OPC UA 服务器，根据指定的位号表进行周期性采集，并将清洗后的数据存入本地 PostgreSQL 时序数据库。

---

## ⚡️ 指令速查表 (Command Cheat Sheet)

### 🟢 日常运行 (High Frequency)
| 任务 | 命令 | 说明 |
| :--- | :--- | :--- |
| **启动采集服务** | `uv run python scheduler.py` | 启动守护进程，周期性采集并入库 |
| **查看数据库** | `psql -U user0 -d opc_lab_data` | 进入数据库命令行 (密码在 config.py) |
| **数据库导出文件** | `pg_dump -U user0 -h localhost opc_lab_data > opc_lab_backup.sql` | 导出为sql文件 |

### 🟡 配置更新 (When Tags Change)
| 任务 | 命令 | 说明 |
| :--- | :--- | :--- |
| **1. 生成位号表** | `uv run python print_nodes.py` | 更新 CSV 位号表 `nodes_list.csv` |
| **2. 生成配置** | `uv run python convert_csv_to_json.py` | 根据 CSV 位号表更新 `nodes.json` |
| **3. 同步数据库** | `uv run python init_db_tags.py` | 将新位号注册到数据库 `tags` 表 |

### 🔵 工具与调试
| 任务 | 命令 | 说明 |
| :--- | :--- | :--- |
| **全量扫描** | `uv run python print_nodes.py` | 扫描服务器所有节点并生成 CSV |
| **手动快照** | `uv run python main.py` | 执行一次性采集并生成 CSV 文件报告 |
| **环境同步** | `uv sync` | 安装/更新项目依赖 |

### 🔧 PID控制
| 任务 | 命令 | 说明 |
| :--- | :--- | :--- |
| **1. IO桥接** | `uv run python io_bridge.py` | 生成 json 桥接文件 |
| **2. 运行PID控制器** | `uv run python pid_controller.py` | 读写对应 json 文件 |

---

## 📂 项目结构

```text
.
├── config.py                   # [核心] 全局配置文件 (IP, 密码, 路径, 周期)
├── control_config.py           # [核心] 控制配置文件 (参数, 桥接文件, 周期)
├── nodes.json                  # [自动生成] 实际采集的节点映射表
├── tracked_tags_values.csv     # [输入] 原始位号表 (来源: Excel整理)
├── scheduler.py                # [主程序] 周期性采集调度器
├── db_manager.py               # [底层] 数据库连接池与 COPY 写入封装
├── client_manager.py           # [底层] OPC UA 连接上下文管理
├── init_db_tags.py             # [工具] 数据库元数据初始化脚本
├── convert_flat_csv_to_json.py # [工具] CSV -> JSON 转换器
└── README.md                   # 项目文档