# HiSilicon & MStar TV Firmware Modding Suite
### Board: `TP.SK508.PB801` | SoC: `Hi3751V350` (Cortex-A53, Android 9 Pie API 28)

This repository contains tools, reverse-engineered scripts, and utilities for unpacking, modifying, repairing, and re-packing firmware binaries (`allupgrade_V351_sos.bin`) for Smart TVs running on HiSilicon and MStar chipsets.

Repository: **[https://github.com/shrinathpol/mstar-bin-tool](https://github.com/shrinathpol/mstar-bin-tool)**

---

## 🛠 Included Tools & Utilities

| Script | Description |
| :--- | :--- |
| **`fix_hd_backlight.py`** | Fixes LED backlight flicker by reprogramming OB3350 dimming PWM from 180Hz to 25kHz with correct GPIO `0x1B` and polarity `0x0`. |
| **`create_fhd_bin.py`** | Automatically builds a 1920×1080 Full HD firmware binary with verified partition CRCs. |
| **`unpack_hisi.py`** | Fast unpacker for HiSilicon `allupgrade_V351_sos.bin` container files and partition CRC32 verification. |
| **`patch_all_final.py`** | Comprehensive patcher for remote keycodes (`key.xml`), hotkeys (`hotkey.xml`), RAM manager (`HiRMService`), and country settings. |
| **`gen_veuwo_logo.py`** | High-definition boot logo generator and injector for Partition 7. |
| **`install_all_apps.py`** | Batch split-APK installer via ADB (`install-multiple`) for Android TV applications. |

---

## 🔬 Key Technical Discoveries & Fixes

### 1. LED Backlight Flickering Fix (`fix_hd_backlight.py`)
* **Hardware Architecture:** The `TP.SK508.PB801` combo board utilizes an **OB3350** LED backlight boost driver IC. An analog RC filter on the DIM pin integrates the PWM signal into a steady DC dimming voltage.
* **The Problem:** Generic 1366×768 panel dumps set the PWM frequency to `180 Hz`, with inverted polarity (`0x3`) on GPIO `0x14`. Because 180 Hz is far too low for the board's filter capacitor, the voltage oscillates, creating visible backlight flickering.
* **The Solution:** 
  - PWM Frequency: Set to `25,000 Hz` (25 kHz).
  - Control Line: Set to GPIO `0x1B`.
  - Polarity: Set to `0x00`.
  - Partition 5 CRC recalculation via GF(2) linear CRC32 algorithms.

### 2. Physical Remote Control & Power Button Fix
* In `/atv/etc/key.xml` and `/vendor/etc/key.xml`:
  - `0xbb447f00` $\rightarrow$ `KEY_HOME` (physical HOME button returns to Launcher)
  - `0x1ce37f00` $\rightarrow$ `KEY_TV_INPUT_MEDIA` (physical FILE button opens File Manager)
  - `0xaa557f00` / `0x19e67f00` $\rightarrow$ `KEY_QUICK_START3` (physical APP button opens "My Apps")
  - `0x9f607f00` $\rightarrow$ `KEY_QUICK_START1` (YouTube shortcut)
  - `0x18e77f00` $\rightarrow$ `KEY_QUICK_START6` (Prime Video shortcut)
  - Power button standby daemon restored in `HiRMService` RAM manager configuration.

### 3. Exit Button & Source Entrapment Fix
* Configured `enable_on_back_pressed=1` and `en_input_source_out_of_tv=0` inside `GlobalUI` configuration:
  - Pressing **EXIT** when in ATV/HDMI source cleanly closes the TV Activity and returns to the Android Home screen.
  - The Input Source popup displays the "Home / Android" option to navigate out of HDMI/AV.

### 4. Package Installer Fix
* In the stock ROM, `com.android.packageinstaller` was disabled (`enabled=0`).
* Fix: Re-enabled via `pm enable com.android.packageinstaller` and granted `REQUEST_INSTALL_PACKAGES` to the TV file manager.

---

## 🚀 How to Use

### Verify and Flash Firmware
1. Copy `allupgrade_V351_sos.bin` to the root of a FAT32-formatted USB pendrive.
2. Insert into the TV's USB port while unplugged.
3. Power on the TV. The front standby LED will blink rapidly for ~2 minutes while partitions are written.
4. The TV will automatically reboot into Android.

---

## 👤 Author
Developed and maintained by **[Shrinath Pol](https://github.com/shrinathpol)**.
