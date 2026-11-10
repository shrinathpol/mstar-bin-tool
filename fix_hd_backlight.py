import struct
import os

CRC_TABLE = [0]*256
for i in range(256):
    c = i << 24
    for _ in range(8):
        c = ((c << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if (c & 0x80000000) else (c << 1) & 0xFFFFFFFF
    CRC_TABLE[i] = c

def hisi_crc(data, crc=0xFFFFFFFF):
    for b in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ CRC_TABLE[((crc >> 24) ^ b) & 0xFF]
    return crc

files = [
    "/mnt/c/Users/Shri1/Downloads/PATCHED_FOR_USB/allupgrade_V351_sos.bin",
    "/mnt/c/Users/Shri1/Downloads/allupgrade_V351_sos.bin",
    "/mnt/e/Unknown/allupgrade_V351_sos.bin"
]

for path in files:
    if not os.path.exists(path):
        print(f"Skipping {path} (does not exist)")
        continue
    print(f"[*] Patching backlight parameters in {path}...")
    with open(path, "r+b") as f:
        f.seek(0x012e6cec)
        sz, old_crc = struct.unpack(">II", f.read(8))
        data = bytearray(f.read(sz))
        
        for idx in range(16):
            off = 0x84 + idx * 0x300
            if off + 0x300 > len(data): break
            data[off + 0x78] = 0x0f
            # 25000 Hz PWM (25 kHz for OB3350 analog RC filter)
            struct.pack_into("<3I", data, off + 0x110, 25000, 25000, 25000)
            data[off + 0x12c] = 0x00
            # GPIO 0x1b for TP.SK508.PB801
            gpios = [0xb0, 0xb0, 0xb0, 0xb0, 0x1b, 0x1b, 0x1b, 0x1b, 0xb0, 0xb0, 0xb0, 0xb0]
            struct.pack_into("<12I", data, off + 0x2cc, *gpios)
        
        new_crc = hisi_crc(data)
        assert new_crc == 0x32a5a7b8
        
        # Write updated header and data
        f.seek(0x012e6cec)
        f.write(struct.pack(">II", sz, new_crc))
        f.write(data)
        print(f"[✓] {path}: P5 CRC updated from 0x{old_crc:08x} -> 0x{new_crc:08x} (25kHz PWM, GPIO 0x1B, Polarity 0x0)")

print("\n[★] All HD firmware files updated with steady 25kHz backlight timing!")
