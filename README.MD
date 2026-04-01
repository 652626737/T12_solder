# T12焊台固件

基于 Arduino 的 T12 焊台控制器，支持 OLED 显示、PID 温度控制、多烙铁头管理。

## 功能特性

- PID 温度控制算法，实现精准控温
- OLED 屏幕显示（支持中文界面）
- 多烙铁头配置管理，自动识别与切换
- 休眠与关机定时器，节能安全
- 温度校准功能，适配不同传感器

## 硬件要求

- 主控：Arduino Nano（ATmega328P）
- 显示屏：SH1106 OLED（128x64）
- 加热元件：T12 烙铁头
- 输入设备：旋转编码器（带按键）
- 其他：MOSFET 驱动模块、电源（24V 推荐）

## 软件依赖

- [PlatformIO](https://platformio.org/)（推荐）或 Arduino IDE
- 库依赖（通过 PlatformIO 自动安装）：
  - U8g2（OLED 驱动）
  - PID 控制库
  - RotaryEncoder

## 编译与上传

### 使用 PlatformIO（推荐）

1. 克隆本仓库
2. 安装 PlatformIO 扩展（VSCode）或命令行工具
3. 编译项目
```bash
platformio run
