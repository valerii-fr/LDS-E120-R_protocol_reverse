# LDS-E120-R protocol

**Version:** 1.0 (December 2025)

**Lidar model:** PaceCat LDS-E120-R

**Interface:** UART TTL 3.3 V

**Status:** fully functional, verified in real-time

### 1. Physical Layer Parameters

- Baud rate: 230400 (default)
- Data format: 8N1
- Read timeout: infinite (blocking)

### 2. Packet Format

| Packet type | Length | Condition |
| --- | --- | --- |
| Regular | 100 B | Sector angle ≠ 0 |
| Final | 108 B | Sector angle = 0 (scan complete) |

**Packet layout (bytes):**

| Offset  | Size | Content                   | Note                    |
|---------|------|---------------------------|-------------------------|
| 0–1     | 2    | Header                    | CF FA (fixed)           |
| 2       | 1    | Points count              | 1E (seems to be fixed)  |
| 3       | 1    | Padding                   | 00 (fixed)              |
| 4–5     | 2    | Sector start angle × 10°  | little-endian uint16    |
| 6–7     | 2    | Angle increment for frame | B4 00 (fixed 18×10°)    |
| 8–97    | 90   | 30 points × 3 bytes       | see below               |
| 98-99   | 2    | probably CRC              | didn't find algo        |
| 100–107 | 8    | Tail (final packet only)  | 53 54 13 00 XX 1A 45 44 |

### 3. Point Format (3 bytes, offset 8 + i×3)

| Byte | Meaning                 |
| --- |-------------------------|
| 0 | Intensity               |
| 1 | Low 8 bits of distance  |
| 2 | High 8 bits of distance |

**Distance calculation (16-bit little-endian):**

```jsx
uint32_t distance_mm = byte0 + (byte2 << 8);
```

**Range:** 50 – 12000 mm (0.05 – 12 m)

### 4. Angle Calculation

```jsx
double sector_angle_deg = sector_uint16 * 0.1;
double point_angle_deg  = sector_angle_deg + index * 0.6;
```

- Sectors per revolution: 20
- Points per sector: 30
- Angular step inside sector: 0.6°
- Total points per revolution: 600
- Angular resolution: 0.6°

### 5. End-of-Scan Detection

- Packet with sector angle = 0 (bytes 4–5 = 00 00)
- Packet length = 108 bytes
- Presence of 8-byte tail

### 6. Point Filtering (current implementation)

```jsx
if (distance_mm < 50 || distance_mm > 12000)   
    discard point
```

### 7. Visualization

- Point cloud: matplotlib.scatter
- Color coding: HSV by intensity
- Connecting line: black, linewidth 1.0, alpha 0.6
- Grid:
    - minor: step 100 mm
    - major: step 1000 mm
- Display area: ±5000 mm

### 8. Termination

- Closing the Matplotlib window
- Ctrl+C in terminal

### 9. Commands

**PaceCat LDS-E120-R Command Set (verified on real hardware, December 2025)**

| Command | Response (example) | Purpose | Working |
| --- | --- | --- | --- |
| LSTOPH | LiDAR STOP! | Stop scanning | Yes |
| LSTARH | LiDAR START! | Start scanning | Yes |
| LUUIDH | PRODUCT SN:LDS-E120-R_A
LUUIDH OK | Query product serial number | Yes |
| LXVERH | MCU VERSION: 0004 <br> MOTOR VERSION: V1.6_230613_R <br> MOTOR HVERSION: V2.2_230223_A <br> CHIPID: 982D534D4C344B0659583141 <br> LXVERH OK | Query firmware and hardware versions | Yes |
| LTYPEH | TYPE ID:LDS-E120-R | Query model identifier | Yes |
| LSRPM:XXXH | LSRPM:400H OK (example) | Set motor speed in RPM (e.g. 400) | Yes* |
- Note: The RPM command is accepted and the motor speed changes, but the data packet format (30 points per sector, 0.6° step) remains unchanged on the tested firmware revision. This can cause points cloud shifts and corrupted map.
- Works well @ 400 RPM
- All commands are terminated with \r\n. The lidar responds with human-readable text followed by OK (or an error message).

### 10. Note

All protocol parameters (packet structure, distance scaling, angular step, tail format) were derived exclusively from analysis of the real UART stream of the PaceCat LDS-E120-R lidar.
BlueSeaLidar projects were used to extract some of protocol related data concerning the command mode of LiDAR.