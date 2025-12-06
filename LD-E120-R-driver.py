#!/usr/bin/env python3
# pacecat_viewer_uuid.py — финальная версия + запрос UUID по команде LUUIDH

import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
import signal
import time

def main():
    parser = argparse.ArgumentParser(description="PaceCat LDS-E120-R — Rainbow by Intensity + LUUIDH command")
    parser.add_argument('-p', '--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('-b', '--baud', type=int, default=230400, help='Baud rate (default: 230400)')
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1.0)  # timeout нужен для чтения ответа
        print(f"[OK] Connected {args.port} @ {args.baud} baud")
    except serial.SerialException as e:
        print(f"[ERROR] cannot open port {args.port}: {e}")
        sys.exit(1)

    HEADER = b'\xCF\xFA'
    FRAME_BASE_LEN = 100
    TAIL_LEN = 8
    ANGLE_INC = 0.6
    MIN_RANGE = 50
    MAX_RANGE = 12000
    MAX_DISPLAY_DIST = 5000

    buffer = bytearray()
    full_scans = 0

    # === ОТПРАВКА КОМАНДЫ LUUIDH ===
    print("[INFO] Sending command: LUUIDH")
    ser.write(b'LUUIDH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LUUIDH")

    print("[INFO] Sending command: LTYPEH")
    ser.write(b'LTYPEH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LTYPEH")

    print("[INFO] Sending command: LXVERH")
    ser.write(b'LXVERH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LXVERH")

    print("[INFO] Sending command: LVERSH")
    ser.write(b'LVERSH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LVERSH")

    print("[INFO] Sending command: LSTOPH")
    ser.write(b'LSTOPH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LSTOPH")
    time.sleep(0.5)

    print("[INFO] Sending command: LSTARH")
    ser.write(b'LSTARH\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LSTARH")

    print("[INFO] Sending command: LSRPM:400H")
    ser.write(b'LSRPM:400H\r\n')  # многие лидары ожидают CR+LF
    time.sleep(0.1)

    # Читаем ответ (обычно до 100 байт)
    response = ser.read(100)
    if response:
        print(f"[RESPONSE] Raw: {response}")
        try:
            print(f"[RESPONSE] Text: {response.decode('utf-8', errors='ignore').strip()}")
        except:
            print("[RESPONSE] <binary or unreadable>")
    else:
        print("[WARNING] No response to LSRPM:400H")

    # === Визуализация ===
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST)
    ax.set_ylim(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST)
    ax.set_aspect('equal')
    ax.set_title("PaceCat LDS-E120-R — Rainbow by Intensity (d0)", fontsize=16)

    # Сетка
    ax.set_xticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 100), minor=True)
    ax.set_yticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 100), minor=True)
    ax.set_xticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 1000), minor=False)
    ax.set_yticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 1000), minor=False)
    ax.grid(True, which='minor', color='#dddddd', linewidth=0.5, alpha=0.7)
    ax.grid(True, which='major', color='#999999', linewidth=1.0, alpha=0.9)
    ax.tick_params(which='minor', labelbottom=False, labelleft=False)

    scatter = ax.scatter([], [], s=10, c=[], cmap='rainbow', vmin=0, vmax=255, alpha=0.9)
    line, = ax.plot([], [], color='black', linewidth=0.8, alpha=0.5)

    x_buf, y_buf, intensity_buf = [], [], []

    print("\nPaceCat LDS-E120-R — running. Close window or Ctrl+C to quit.\n")

    running = True

    def close_handler(event):
        nonlocal running
        print("\n[INFO] Window closed — stopping...")
        running = False

    def signal_handler(signum, frame):
        nonlocal running
        print("\n[INFO] Ctrl+C — stopping...")
        running = False

    fig.canvas.mpl_connect('close_event', close_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        while running:
            data = ser.read(2048)
            if data:
                buffer.extend(data)

            while running:
                pos = buffer.find(HEADER)
                if pos == -1 or len(buffer) < pos + FRAME_BASE_LEN:
                    if pos != -1:
                        buffer = buffer[pos:]
                    break

                sector_raw = struct.unpack_from('<H', buffer, pos + 4)[0]
                sector_deg = sector_raw / 10.0
                is_zero = (sector_raw == 0)
                frame_len = FRAME_BASE_LEN + (TAIL_LEN if is_zero else 0)

                if len(buffer) < pos + frame_len:
                    buffer = buffer[pos:]
                    break

                frame = buffer[pos: pos + frame_len]
                buffer = buffer[pos + frame_len:]

                for i in range(30):
                    off = 8 + i * 3
                    intensity = frame[off]           # d0 — intensity
                    d1 = frame[off + 1]
                    d2 = frame[off + 2]
                    dist_mm = d1 + (d2 << 8)          # миллиметры напрямую

                    angle_deg = sector_deg + i * ANGLE_INC
                    rad = np.radians(angle_deg)

                    if MIN_RANGE <= dist_mm <= MAX_RANGE:
                        x = dist_mm * np.cos(rad)
                        y = dist_mm * np.sin(rad)
                        x_buf.append(x)
                        y_buf.append(y)
                        intensity_buf.append(intensity)

                if is_zero:
                    full_scans += 1
                    tail = frame[100:108]
                    print(f"\n=== TURN #{full_scans} ===  ({len(x_buf)} pts)")
                    print(f"Tail: {' '.join(f'{b:02X}' for b in tail)}")

                    if x_buf:
                        scatter.set_offsets(np.c_[x_buf, y_buf])
                        scatter.set_array(np.array(intensity_buf))
                        line.set_data(x_buf, y_buf)
                        fig.canvas.draw_idle()
                        fig.canvas.flush_events()

                    x_buf.clear()
                    y_buf.clear()
                    intensity_buf.clear()

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ser.close()
        plt.ioff()
        plt.close('all')
        print("[INFO] Stopped.")

if __name__ == '__main__':
    main()