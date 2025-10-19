"""
SG90舵机控制模块

SG90参数:
- 工作电压: 4.8V-6V
- 控制信号: PWM 50Hz
- 脉冲宽度: 0.5ms(0°) ~ 2.5ms(180°)
- 转动角度: 0-180°
"""

import logging
import time
import threading
from typing import Optional, Dict, Any

# 尝试导入pigpio（硬件PWM）
try:
    import pigpio

    PIGPIO_AVAILABLE = True
except ImportError:
    PIGPIO_AVAILABLE = False
    pigpio = None


class SG90Servo:
    """SG90舵机控制类"""

    # PWM参数
    PWM_FREQUENCY = 50  # 50Hz
    PULSE_MIN = 500  # 0.5ms = 500us
    PULSE_MAX = 2500  # 2.5ms = 2500us
    ANGLE_MIN = 0  # 最小角度
    ANGLE_MAX = 180  # 最大角度

    def __init__(self, pin: int = 18):
        """
        初始化SG90舵机

        Args:
            pin: GPIO引脚号（推荐使用GPIO 18，支持硬件PWM）
        """
        self.pin = pin
        self.current_angle = 90  # 当前角度
        self.target_angle = 90  # 目标角度
        self.enabled = False  # 舵机启用状态
        self.scanning = False  # 扫描状态
        self.scan_thread = None  # 扫描线程

        self.logger = logging.getLogger(__name__)

        # 初始化pigpio
        self.pi = None
        if PIGPIO_AVAILABLE:
            try:
                self.pi = pigpio.pi()
                if not self.pi.connected:
                    self.logger.warning("pigpio daemon not running")
                    self.pi = None
                else:
                    self.logger.info(f"pigpio connected for servo on GPIO {self.pin}")
            except Exception as e:
                self.logger.error(f"Failed to connect to pigpio: {e}")
                self.pi = None
        else:
            self.logger.warning("pigpio not available, servo control disabled")

    def _angle_to_pulse_width(self, angle: float) -> int:
        """
        将角度转换为脉冲宽度（微秒）

        Args:
            angle: 角度 (0-180)

        Returns:
            脉冲宽度（微秒）
        """
        # 限制角度范围
        angle = max(self.ANGLE_MIN, min(self.ANGLE_MAX, angle))

        # 线性映射: 0° -> 500us, 180° -> 2500us
        pulse_width = self.PULSE_MIN + (angle / self.ANGLE_MAX) * (
            self.PULSE_MAX - self.PULSE_MIN
        )
        return int(pulse_width)

    def _pulse_width_to_angle(self, pulse_width: int) -> float:
        """
        将脉冲宽度转换为角度

        Args:
            pulse_width: 脉冲宽度（微秒）

        Returns:
            角度 (0-180)
        """
        angle = (
            (pulse_width - self.PULSE_MIN)
            * self.ANGLE_MAX
            / (self.PULSE_MAX - self.PULSE_MIN)
        )
        return round(angle, 1)

    def _calculate_duty_cycle(self, pulse_width: int) -> float:
        """
        计算占空比

        Args:
            pulse_width: 脉冲宽度（微秒）

        Returns:
            占空比（百分比）
        """
        # 周期 = 1/50Hz = 20ms = 20000us
        period = 1000000 / self.PWM_FREQUENCY
        duty_cycle = (pulse_width / period) * 100
        return round(duty_cycle, 2)

    def enable(self) -> Dict[str, Any]:
        """启用舵机"""
        if not self.pi:
            return {"success": False, "error": "pigpio not available"}

        try:
            # 设置PWM频率
            self.pi.set_PWM_frequency(self.pin, self.PWM_FREQUENCY)

            # 移动到当前角度（默认90度）
            self.set_angle(self.current_angle)

            self.enabled = True
            self.logger.info(f"Servo enabled on GPIO {self.pin}")

            return {
                "success": True,
                "message": "Servo enabled",
                "angle": self.current_angle,
            }
        except Exception as e:
            self.logger.error(f"Failed to enable servo: {e}")
            return {"success": False, "error": str(e)}

    def disable(self) -> Dict[str, Any]:
        """禁用舵机"""
        if not self.pi:
            return {"success": False, "error": "pigpio not available"}

        try:
            # 停止扫描
            self.stop_scan()

            # 停止PWM输出
            self.pi.set_PWM_dutycycle(self.pin, 0)

            self.enabled = False
            self.logger.info(f"Servo disabled on GPIO {self.pin}")

            return {"success": True, "message": "Servo disabled"}
        except Exception as e:
            self.logger.error(f"Failed to disable servo: {e}")
            return {"success": False, "error": str(e)}

    def set_angle(self, angle: float, smooth: bool = False) -> Dict[str, Any]:
        """
        设置舵机角度

        Args:
            angle: 目标角度 (0-180)
            smooth: 是否平滑移动

        Returns:
            操作结果
        """
        if not self.pi:
            return {"success": False, "error": "pigpio not available"}

        if not self.enabled:
            return {"success": False, "error": "Servo not enabled"}

        try:
            # 限制角度范围
            angle = max(self.ANGLE_MIN, min(self.ANGLE_MAX, angle))
            self.target_angle = angle

            # 计算脉冲宽度
            pulse_width = self._angle_to_pulse_width(angle)

            # 如果启用平滑移动
            if smooth and abs(angle - self.current_angle) > 5:
                self._smooth_move(angle)
            else:
                # 直接设置
                self.pi.set_servo_pulsewidth(self.pin, pulse_width)
                self.current_angle = angle

            # 计算参数
            duty_cycle = self._calculate_duty_cycle(pulse_width)

            self.logger.info(
                f"Servo angle set to {angle}° (pulse: {pulse_width}us, duty: {duty_cycle}%)"
            )

            return {
                "success": True,
                "angle": self.current_angle,
                "target_angle": self.target_angle,
                "pulse_width": pulse_width / 1000,  # 转换为ms
                "duty_cycle": duty_cycle,
            }
        except Exception as e:
            self.logger.error(f"Failed to set servo angle: {e}")
            return {"success": False, "error": str(e)}

    def _smooth_move(self, target_angle: float, step: float = 2.0, delay: float = 0.02):
        """
        平滑移动到目标角度

        Args:
            target_angle: 目标角度
            step: 每步移动的角度
            delay: 每步之间的延迟（秒）
        """
        while abs(self.current_angle - target_angle) > step:
            if self.current_angle < target_angle:
                self.current_angle += step
            else:
                self.current_angle -= step

            pulse_width = self._angle_to_pulse_width(self.current_angle)
            self.pi.set_servo_pulsewidth(self.pin, pulse_width)
            time.sleep(delay)

        # 最后精确到达目标
        self.current_angle = target_angle
        pulse_width = self._angle_to_pulse_width(target_angle)
        self.pi.set_servo_pulsewidth(self.pin, pulse_width)

    def step_move(self, step: float) -> Dict[str, Any]:
        """
        步进移动

        Args:
            step: 移动步长（正数前进，负数后退）

        Returns:
            操作结果
        """
        new_angle = self.current_angle + step
        return self.set_angle(new_angle)

    def start_scan(
        self, start_angle: float = 0, end_angle: float = 180, speed: str = "medium"
    ) -> Dict[str, Any]:
        """
        开始扫描模式

        Args:
            start_angle: 起始角度
            end_angle: 结束角度
            speed: 扫描速度 (slow/medium/fast)

        Returns:
            操作结果
        """
        if not self.enabled:
            return {"success": False, "error": "Servo not enabled"}

        if self.scanning:
            return {"success": False, "error": "Already scanning"}

        # 速度映射到延迟时间
        speed_map = {"slow": 0.05, "medium": 0.03, "fast": 0.01}
        delay = speed_map.get(speed, 0.03)

        self.scanning = True
        self.scan_thread = threading.Thread(
            target=self._scan_worker, args=(start_angle, end_angle, delay), daemon=True
        )
        self.scan_thread.start()

        self.logger.info(
            f"Scan started: {start_angle}° to {end_angle}° at {speed} speed"
        )

        return {
            "success": True,
            "message": "Scan started",
            "start_angle": start_angle,
            "end_angle": end_angle,
            "speed": speed,
        }

    def _scan_worker(self, start_angle: float, end_angle: float, delay: float):
        """扫描工作线程"""
        direction = 1  # 1: 前进, -1: 后退
        current = start_angle
        step = 2.0  # 每步2度

        while self.scanning:
            # 设置角度
            pulse_width = self._angle_to_pulse_width(current)
            self.pi.set_servo_pulsewidth(self.pin, pulse_width)
            self.current_angle = current

            # 移动到下一个位置
            current += step * direction

            # 到达边界，反向
            if current >= end_angle:
                current = end_angle
                direction = -1
            elif current <= start_angle:
                current = start_angle
                direction = 1

            time.sleep(delay)

    def stop_scan(self) -> Dict[str, Any]:
        """停止扫描"""
        if not self.scanning:
            return {"success": True, "message": "Not scanning"}

        self.scanning = False

        # 等待线程结束
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1.0)

        self.logger.info("Scan stopped")

        return {
            "success": True,
            "message": "Scan stopped",
            "current_angle": self.current_angle,
        }

    def emergency_stop(self) -> Dict[str, Any]:
        """急停"""
        self.stop_scan()
        return self.disable()

    def get_status(self) -> Dict[str, Any]:
        """获取舵机状态"""
        pulse_width = self._angle_to_pulse_width(self.current_angle)
        duty_cycle = self._calculate_duty_cycle(pulse_width)

        return {
            "success": True,
            "pin": self.pin,
            "enabled": self.enabled,
            "current_angle": self.current_angle,
            "target_angle": self.target_angle,
            "pulse_width": pulse_width / 1000,  # ms
            "duty_cycle": duty_cycle,
            "frequency": self.PWM_FREQUENCY,
            "scanning": self.scanning,
            "pigpio_available": self.pi is not None,
            "timestamp": time.strftime("%H:%M:%S"),
        }

    def cleanup(self):
        """清理资源"""
        self.stop_scan()
        if self.pi:
            try:
                self.pi.set_PWM_dutycycle(self.pin, 0)
                self.pi.stop()
                self.logger.info("Servo cleanup completed")
            except Exception as e:
                self.logger.warning(f"Servo cleanup warning: {e}")
            finally:
                self.pi = None
