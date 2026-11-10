import struct
import shutil

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

orig_bin = "/mnt/c/Users/Shri1/Downloads/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/allupgrade_V351_sos.bin"
src_patched_bin = "/mnt/c/Users/Shri1/Downloads/PATCHED_FOR_USB/allupgrade_V351_sos.bin"
fhd_bin = "/mnt/c/Users/Shri1/Downloads/allupgrade_V351_sos_FHD_1920x1080.bin"

print("[*] Copying patched bin as base for FHD build...")
shutil.copyfile(src_patched_bin, fhd_bin)

print("[*] Reading original Full HD (1920x1080) panelparam from orig_bin...")
with open(orig_bin, "rb") as fo:
    fo.seek(0x012e6cec)
    fhd_panel_chunk = fo.read(8 + 0x6684)

sz, crc = struct.unpack(">II", fhd_panel_chunk[:8])
assert sz == 0x6684
assert crc == 0x2b83e547
print(f"[+] FHD panelparam verified: size=0x{sz:x}, crc=0x{crc:08x}")

print("[*] Writing Full HD panelparam into fhd_bin at 0x012e6cec...")
with open(fhd_bin, "r+b") as ft:
    ft.seek(0x012e6cec)
    ft.write(fhd_panel_chunk)

print("[*] Verifying all key partitions in fhd_bin...")
with open(fhd_bin, "rb") as ft:
    # 1. P5 panelparam
    ft.seek(0x012e6cec)
    p5_sz, p5_crc = struct.unpack(">II", ft.read(8))
    p5_data = ft.read(p5_sz)
    assert hisi_crc(p5_data) == p5_crc == 0x2b83e547
    print("[✓] P5 (Full HD 1920x1080 panelparam): CRC 0x2b83e547 verified!")

    # 2. P7 logo
    ft.seek(0x014ed380)
    p7_sz, p7_crc = struct.unpack(">II", ft.read(8))
    p7_data = ft.read(p7_sz)
    assert hisi_crc(p7_data) == p7_crc == 0x662b9627
    print("[✓] P7 (VEUWO Boot Logo): CRC 0x662b9627 verified!")

    # 3. P14 system (en-IN)
    ft.seek(0x020c1592)
    p14_sz, p14_crc = struct.unpack(">II", ft.read(8))
    p14_data = ft.read(p14_sz)
    assert hisi_crc(p14_data) == p14_crc == 0xf93a09be
    print("[✓] P14 (System en-IN): CRC 0xf93a09be verified!")

    # 4. P15 vendor
    ft.seek(0x3d00365e)
    p15_sz, p15_crc = struct.unpack(">II", ft.read(8))
    p15_data = ft.read(p15_sz)
    assert hisi_crc(p15_data) == p15_crc == 0x365bd74d
    print("[✓] P15 (Vendor RR pro CH.UNI-201 + Configs): CRC 0x365bd74d verified!")

    # 5. P16 atv
    ft.seek(0x48a56742)
    p16_sz, p16_crc = struct.unpack(">II", ft.read(8))
    p16_data = ft.read(p16_sz)
    assert hisi_crc(p16_data) == p16_crc == 0x5cf09ee8
    print("[✓] P16 (ATV key.xml): CRC 0x5cf09ee8 verified!")

print(f"\n[★] SUCCESS: Full HD (1920x1080) firmware successfully created at: {fhd_bin}")

