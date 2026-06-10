# miHoYoClock — 米哈游辉光管立牌兼容固件

Fork 自 [EleksTubeIPS](https://github.com/judge2005/EleksTubeIPS)。为 miHoYo 2024 年周年庆礼品「拟辉光管立牌」适配的开源固件。

## 硬件信息

| 项目 | 规格 |
|------|------|
| 主控 | ESP32-D0WDR2-V3 |
| Flash | 8MB |
| PSRAM | 2MB |
| 显示屏 | 6 × ST7789 135×240 IPS |
| FPC 引脚 | MOSI=GPIO32, SCLK=GPIO33, DC=GPIO25, RST=GPIO26 |
| CS 引脚 | GPIO15, GPIO2, GPIO27, GPIO14, GPIO12, GPIO13 |
| LED | WS2812 (GPIO5) |
| RTC | DS1302 |

## 编译 & 烧录

```bash
# 安装 PlatformIO
pip install platformio

# 编译
pio run -e mihoyo

# 构建文件系统
pio run -e mihoyo -t buildfs

# 烧录（进入下载模式：按住 SW1 → 插 USB → 松 SW1）
esptool.py --port /dev/cu.usbserial-xxx write_flash \
  0x1000 .pio/build/mihoyo/bootloader.bin \
  0x8000 .pio/build/mihoyo/partitions.bin \
  0x10000 .pio/build/mihoyo/firmware.bin \
  0x180000 .pio/build/mihoyo/littlefs.bin
```

## 启动后

设备会创建 WiFi 热点 **EleksTubeIPS**，密码 `secretsauce`。连上后浏览器打开 `http://192.168.4.1` 配置 WiFi，之后即可通过 Web 界面或 WebSocket (`ws://<ip>/ws`) 控制。

## License

GPL v3，继承自 EleksTubeIPS。

---

# miHoYoClock — Custom Firmware for miHoYo Glow-Tube Stand

Forked from [EleksTubeIPS](https://github.com/judge2005/EleksTubeIPS). Open-source firmware adapted for the miHoYo 2024 anniversary "nixie-tube-style" display stand.

## Hardware

| Item | Spec |
|------|------|
| MCU | ESP32-D0WDR2-V3 |
| Flash | 8MB |
| PSRAM | 2MB |
| Display | 6 × ST7789 135×240 IPS |
| FPC Pins | MOSI=GPIO32, SCLK=GPIO33, DC=GPIO25, RST=GPIO26 |
| CS Pins | GPIO15, GPIO2, GPIO27, GPIO14, GPIO12, GPIO13 |
| LED | WS2812 (GPIO5) |
| RTC | DS1302 |

## Build & Flash

```bash
pip install platformio
pio run -e mihoyo
pio run -e mihoyo -t buildfs

# Enter download mode: hold SW1 → plug USB → release SW1
esptool.py --port /dev/cu.usbserial-xxx write_flash \
  0x1000 .pio/build/mihoyo/bootloader.bin \
  0x8000 .pio/build/mihoyo/partitions.bin \
  0x10000 .pio/build/mihoyo/firmware.bin \
  0x180000 .pio/build/mihoyo/littlefs.bin
```

## First Boot

The device creates a WiFi AP named **EleksTubeIPS** (password: `secretsauce`). Connect and open `http://192.168.4.1` to configure WiFi. After connecting, use the web UI or WebSocket (`ws://<ip>/ws`) for control.

## License

GPL v3, inherited from EleksTubeIPS.
