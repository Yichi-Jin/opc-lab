# control_config.py
class ControlConfig:
    # OPC UA 服务器地址
    "opc.tcp://127.0.0.1:4840"
    
    # 刷新频率 (秒) - 控制回路通常需要更快的频率
    LOOP_RATE = 1

 # === 文件路径 ===
    STATE_FILE = "io_state.json"      # 输入：当前设备状态 (PV)
    COMMAND_FILE = "io_command.json"  # 输出：控制指令 (MV)

    # === IO 映射 ===
    TAGS = {
        "LI104_PV": "ns=1;s=LI104.PV",   # 液位 (0-45cm)
        "FIC101_MV": "ns=1;s=FIC101_1.MV" # 进水阀 (0-100%)
    }

    # === PID 控制参数 (新增) ===
    # 设定值 (Setpoint)
    PID_SV = 20.0  # 目标液位 cm
    
    # PID 参数 (需要根据实际系统调试)
    # 建议初始值：P=2.0, I=0.1, D=0.0
    PID_KP = 2.0
    PID_KI = 0.1
    PID_KD = 0.05
    
    # 积分限幅 (防止积分饱和 Windup)
    PID_I_MAX = 50.0 
    PID_I_MIN = -50.0
    
    # 安全限制
    PV_MAX = 45.0  # 液位传感器最大量程
    MV_MIN = 0.0   # 阀门全关
    MV_MAX = 100.0 # 阀门全开