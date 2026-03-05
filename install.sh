#!/bin/bash

echo "🚀 开始初始化 OPC-LAB 环境..."

# 1. 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "⚠️  未检测到 uv，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
else
    echo "✅ 检测到 uv"
fi

# 2. 同步依赖
echo "📦 正在安装 Python 依赖..."
uv sync

# 3. 检查配置文件
if [ ! -f "config.py" ]; then
    echo "⚠️  未找到 config.py。请参考 config_example.py 创建。"
else
    echo "✅ 配置文件已存在"
fi

if [ ! -f "control_config.py" ]; then
    echo "⚠️  未找到 control_config.py。请参考文档创建。"
else
    echo "✅ 控制配置文件已存在"
fi

# 4. 赋予脚本执行权限
chmod +x scheduler.py io_bridge.py pid_controller.py

echo "🎉 安装完成！你可以使用 'uv run python scheduler.py' 启动采集。"