import subprocess
import os
import sys

ADB = "/tmp/platform-tools/adb"

apps = [
    ("Projectivy Launcher", [
        "/mnt/c/Users/Shri1/Downloads/projectapk/base.apk",
        "/mnt/c/Users/Shri1/Downloads/projectapk/split_config.armeabi_v7a.apk",
        "/mnt/c/Users/Shri1/Downloads/projectapk/split_config.xhdpi.apk"
    ]),
    ("YouTube for Android TV", [
        "/mnt/c/Users/Shri1/Downloads/youtube/base.apk",
        "/mnt/c/Users/Shri1/Downloads/youtube/split_config.armeabi_v7a.apk"
    ]),
    ("Amazon Prime Video", [
        "/mnt/c/Users/Shri1/Downloads/ame/base.apk",
        "/mnt/c/Users/Shri1/Downloads/ame/split_config.armeabi_v7a.apk",
        "/mnt/c/Users/Shri1/Downloads/ame/split_config.en.apk",
        "/mnt/c/Users/Shri1/Downloads/ame/split_config.hi.apk",
        "/mnt/c/Users/Shri1/Downloads/ame/split_config.xhdpi.apk"
    ]),
    ("Google Play Store", [
        "/mnt/c/Users/Shri1/Downloads/playstore/base.apk",
        "/mnt/c/Users/Shri1/Downloads/playstore/split_config.armeabi_v7a.apk",
        "/mnt/c/Users/Shri1/Downloads/playstore/split_config.en.apk",
        "/mnt/c/Users/Shri1/Downloads/playstore/split_config.hi.apk"
    ])
]

print("[*] Verifying ADB connection...")
subprocess.run([ADB, "connect", "192.168.1.38:5555"], check=True)

for name, apks in apps:
    print(f"\n[*] Installing {name}...")
    # Check if all files exist
    if not all(os.path.exists(f) for f in apks):
        print(f"[-] Missing files for {name}")
        continue
    cmd = [ADB, "install-multiple", "-r", "-d"] + apks
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode != 0:
        print("ERR:", res.stderr.strip())

print("\n[*] Installing NetMirrorTV...")
netmirror = "/mnt/c/Users/Shri1/Downloads/NetMirrorTV.apk"
if os.path.exists(netmirror):
    res = subprocess.run([ADB, "install", "-r", "-d", netmirror], capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode != 0:
        print("ERR:", res.stderr.strip())

print("\n[✓] All app installations finished.")
