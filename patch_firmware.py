import os
import shutil

SRC_BIN = "/mnt/c/Users/Shri1/Downloads/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/allupgrade_V351_sos.bin"
OUT_BIN = "/mnt/c/Users/Shri1/Downloads/allupgrade_V351_sos_patched_1366x768.bin"

print(f"[*] Reading source firmware: {SRC_BIN}...")
with open(SRC_BIN, "rb") as f:
    data = bytearray(f.read())

# Partition 4 in Unionaire:
# Offset: 0x012e6cec + 8
p4_offset = 0x012e6cec + 8
p4_size = 0x6684 - 8

print(f"[*] Locating Partition 4 (paneldatabody) at 0x{p4_offset:08X}...")

# In Partition 4:
# index0 starts at 0x84, size is 0x300 (0x84 to 0x384)
# index2 starts at 0x684, size is 0x300 (1366x768 60Hz 2D)
idx0_offset = p4_offset + 0x84
idx1_offset = p4_offset + 0x384
idx2_offset = p4_offset + 0x684

idx2_data = bytes(data[idx2_offset : idx2_offset + 0x300])

print("[*] Copying 1366x768 Single-Channel LVDS timing from index2 into index0 and index1...")
# Modify index name for index0 to match "index0" prefix
idx0_patched = bytearray(idx2_data)
idx0_patched[0:7] = b"index0\x00"

idx1_patched = bytearray(idx2_data)
idx1_patched[0:7] = b"index1\x00"

data[idx0_offset : idx0_offset + 0x300] = idx0_patched
data[idx1_offset : idx1_offset + 0x300] = idx1_patched

print(f"[*] Writing patched firmware to: {OUT_BIN}...")
with open(OUT_BIN, "wb") as f:
    f.write(data)

print(f"[✓] SUCCESS! Created patched firmware ({os.path.getsize(OUT_BIN)} bytes).")

