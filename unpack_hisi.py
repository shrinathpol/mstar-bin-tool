import os
import struct

BIN_PATH = "/mnt/c/Users/Shri1/Downloads/TP.SK508.PB801-1366x768-1G-8G-REF75-Skyline/TP.SK508.PB801-1366x768-1G-8G-REF75-Skyline/allupgrade_V351_sos.bin"
OUT_DIR = "./unpacked_hisi"

PARTITION_NAMES = {
    0: "fastboot.bin",
    1: "bootargs.bin",
    2: "slaveboot.bin",
    3: "boot.img",
    4: "atv_channel.bin",
    5: "trustedcore.bin",
    6: "dtv_channel.bin",
    7: "recovery.img",
    8: "bootmusic.img",
    9: "panel_data.bin",
    10: "deviceinfo.bin",
    11: "baseparam.bin",
    12: "pqparam.bin",
    13: "logo.img",
    14: "system.img",
    15: "vendor.img",
    16: "userdata.img",
    17: "cache.img",
    18: "factorydata.bin"
}

os.makedirs(OUT_DIR, exist_ok=True)

with open(BIN_PATH, "rb") as f:
    hdr = f.read(0x400)
    
    if hdr[:5] != b"LOADT":
        print("[!] Error: Not a valid HiSilicon LOADT firmware package!")
        exit(1)
        
    print("[*] Valid HiSilicon firmware detected. Parsing partition table...")
    
    for i in range(19):
        entry = hdr[0x40 + i * 0x20 : 0x40 + (i + 1) * 0x20]
        vals = struct.unpack(">8I", entry)
        
        flash_start = vals[0]
        flash_end = vals[2]
        part_size = vals[5]
        file_offset = vals[6]
        
        part_name = PARTITION_NAMES.get(i, f"partition_{i}.img")
        out_path = os.path.join(OUT_DIR, part_name)
        
        print(f"\n[+] Extracting {part_name}:")
        print(f"    Offset: 0x{file_offset:08X} | Size: {c  / (1024*1024):.2f} MB")
        
        f.seek(file_offset)
        chunk_hdr = f.read(8)
        
        payload_size = part_size - 8
        with open(out_path, "wb") as out_f:
            remaining = payload_size
            buf_size = 8 * 1024 * 1024
            while remaining > 0:
                to_read = min(remaining, buf_size)
                buf = f.read(to_read)
                if not buf:
                    break
                out_f.write(buf)
                remaining -= len(buf)
                
        print(f"    Saved -> {out_path}")

print("\n[*] All partitions extracted successfully to:", OUT_DIR)

