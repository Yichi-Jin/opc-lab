import json
import time
import os
import asyncio
from control_config import ControlConfig

class PID:
    """简易 PID 算法实现"""
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        # 内部状态
        self._last_error = 0.0
        self._integral = 0.0
        self._last_time = time.time()
        
    def update(self, current_value):
        """
        计算一步 PID
        :param current_value: 当前 PV 值
        :return: 控制量 MV
        """
        now = time.time()
        dt = now - self._last_time
        if dt <= 0: dt = 1e-16 # 防止除零

        # 1. 计算误差 (反作用: 需要加水则 Error > 0)
        error = self.setpoint - current_value
        
        # 2. 比例项 (P)
        p_term = self.kp * error
        
        # 3. 积分项 (I)
        self._integral += error * dt
        # 积分限幅 (Anti-windup)
        self._integral = max(ControlConfig.PID_I_MIN, min(ControlConfig.PID_I_MAX, self._integral))
        i_term = self.ki * self._integral
        
        # 4. 微分项 (D)
        delta_error = error - self._last_error
        d_term = self.kd * (delta_error / dt)
        
        # 5. 总输出
        output = p_term + i_term + d_term
        
        # 更新状态
        self._last_error = error
        self._last_time = now
        
        return output

async def control_loop():
    # 1. 安全检查：确保设定值在物理范围内
    safe_sv = max(0.0, min(ControlConfig.PV_MAX, ControlConfig.PID_SV))
    print(f"🎛️  PID 控制器启动")
    print(f"    目标设定值 (SV): {safe_sv} cm")
    print(f"    参数: Kp={ControlConfig.PID_KP}, Ki={ControlConfig.PID_KI}, Kd={ControlConfig.PID_KD}")

    # 初始化 PID 对象
    pid = PID(ControlConfig.PID_KP, ControlConfig.PID_KI, ControlConfig.PID_KD, safe_sv)
    
    while True:
        cycle_start = time.time()
        
        try:
            # ===========================
            # 1. 获取反馈 (Read PV)
            # ===========================
            if not os.path.exists(ControlConfig.STATE_FILE):
                print("⏳ 等待 IO 数据...")
                await asyncio.sleep(1)
                continue
                
            with open(ControlConfig.STATE_FILE, 'r') as f:
                state = json.load(f)
            
            # 检查数据时效性 (例如超过 5秒没更新视为断线)
            if time.time() - state.get("_timestamp", 0) > 5.0:
                print("⚠️  警告: 数据已过期，停止控制")
                # 可选：这里可以选择保持输出或强制关闭阀门
                await asyncio.sleep(1)
                continue

            pv = state.get("LI104_PV")
            
            if pv is None:
                print("⚠️  未获取到液位 PV")
                continue

            # ===========================
            # 2. 计算输出 (Compute PID)
            # ===========================
            # 确保 PV 输入有效
            safe_pv = max(0.0, min(ControlConfig.PV_MAX, float(pv)))
            
            # 计算原始输出
            raw_mv = pid.update(safe_pv)
            
            # 输出限幅 (Clamping 0-100%)
            final_mv = max(ControlConfig.MV_MIN, min(ControlConfig.MV_MAX, raw_mv))

            # 打印调试信息
            print(f"🎯 SV={safe_sv:.1f} | 🌊 PV={safe_pv:.2f} | 🔧 MV={final_mv:.2f}% (P:{pid.kp*(safe_sv-safe_pv):.1f} I:{pid._integral*pid.ki:.1f})")

            # ===========================
            # 3. 发送指令 (Write MV)
            # ===========================
            command = {
                "FIC101_MV": final_mv
            }
            
            # 原子写入 command.json
            temp_file = ControlConfig.COMMAND_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(command, f)
            os.replace(temp_file, ControlConfig.COMMAND_FILE)

        except Exception as e:
            print(f"❌ 控制回路错误: {e}")
        
        # ===========================
        # 4. 保持控制周期
        # ===========================
        elapsed = time.time() - cycle_start
        sleep_time = max(0, ControlConfig.LOOP_RATE - elapsed)
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    try:
        asyncio.run(control_loop())
    except KeyboardInterrupt:
        print("\n🛑 PID 控制器已停止")