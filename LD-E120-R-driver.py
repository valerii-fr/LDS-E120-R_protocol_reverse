#!/usr/bin/env python3

import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import argparse
import sys
import signal

## FRAME
## [HEADER   ] [ANGLE x10] [SIGNATURE] [30 PTS] [TAIL]
## CF FA 1E 00    B4 00       B4 00    D1 D2 D3
## fixed           180        fixed    24 bits

## TAIL
## [SIGNATURE] [INCREMENT] [SIGNATURE]
## 53 54 13 00     16       1A 45 44
##    fixed      unknown     fixed

def main():
    parser = argparse.ArgumentParser(
        description="PaceCat LDS-E120-R demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""How to use:
  %(prog)s -p COM3
  %(prog)s --port /dev/ttyUSB0 --baud 230400"""
    )
    parser.add_argument('-p', '--port', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('-b', '--baud', type=int, default=230400, help='Baud rate (default: 230400)')
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=None)
        print(f"[OK] Connected {args.port} @ {args.baud} baud")
    except serial.SerialException as e:
        print(f"[ERROR] cannot open port {args.port}: {e}")
        sys.exit(1)

    HEADER = b'\xCF\xFA\x1E\x00'
    FRAME_BASE_LEN = 100
    TAIL_LEN = 8
    SCALE = 256
    ANGLE_INC = 0.6
    POINTS_COUNT = 30
    MIN_RANGE = 50
    MAX_RANGE = 12000
    MAX_DISPLAY_DIST = 5000

    buffer = bytearray()
    full_scans = 0

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST)
    ax.set_ylim(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST)
    ax.set_aspect('equal')
    ax.set_title("PaceCat LDS-E120-R (600 pts/scan)", fontsize=16)

    # Сетка
    ax.set_xticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 100), minor=True)
    ax.set_yticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 100), minor=True)
    ax.set_xticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 1000), minor=False)
    ax.set_yticks(np.arange(-MAX_DISPLAY_DIST, MAX_DISPLAY_DIST + 1, 1000), minor=False)
    ax.grid(True, which='minor', color='#dddddd', linewidth=0.5, alpha=0.7)
    ax.grid(True, which='major', color='#999999', linewidth=1.0, alpha=0.9)
    ax.tick_params(which='minor', labelbottom=False, labelleft=False)

    scatter = ax.scatter([], [], s=8, c=[], alpha=0.9)
    line, = ax.plot([], [], color='black', linewidth=1.0, alpha=0.6)

    x_buf, y_buf, hue_buf = [], [], []

    print("PaceCat LDS-E120-R is running. Close window or Ctrl+C to quit.\n")

    # Флаг завершения
    running = True

    def close_handler(event):
        nonlocal running
        print("\n[INFO] Window is closed - stopping...")
        running = False

    def signal_handler(signum, frame):
        nonlocal running
        print("\n[INFO] Received Ctrl+C - stopping...")
        running = False

    fig.canvas.mpl_connect('close_event', close_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        while running:
            data = ser.read(1024)
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

                for i in range(POINTS_COUNT):
                    off = 8 + i * 3
                    d0, d1, d2 = frame[off], frame[off+1], frame[off+2]
                    raw = d0 + (d1 << 8) + (d2 << 16)
                    dist_mm = raw // SCALE

                    angle_deg = sector_deg + i * ANGLE_INC
                    rad = np.radians(angle_deg)

                    if MIN_RANGE <= dist_mm <= MAX_RANGE:
                        x = dist_mm * np.cos(rad)
                        y = dist_mm * np.sin(rad)
                        x_buf.append(x)
                        y_buf.append(y)
                        hue_buf.append(angle_deg % 360)

                if is_zero:
                    full_scans += 1
                    tail = frame[100:108]
                    print(f"\n=== TURN #{full_scans} ===  ({len(x_buf)} pts)")
                    print(f"Tail: {' '.join(f'{b:02X}' for b in tail)}")

                    if x_buf:
                        scatter.set_offsets(np.c_[x_buf, y_buf])
                        colors = [hsv_to_rgb([h/360, 1.0, 1.0]) for h in hue_buf]
                        scatter.set_color(colors)
                        line.set_data(x_buf, y_buf)
                        fig.canvas.draw_idle()
                        fig.canvas.flush_events()

                    x_buf.clear()
                    y_buf.clear()
                    hue_buf.clear()

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ser.close()
        plt.ioff()
        plt.close('all')
        print("[INFO] Stopped.")

if __name__ == '__main__':
    main()