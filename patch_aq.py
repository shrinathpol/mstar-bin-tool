#!/usr/bin/env python3
import sys

def patch_aq():
    with open('/home/shrinathpol/mstar-bin-tool/aq.ini', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Patch GEQ in all sound modes
    old_geq = """standard = 50, 50, 50, 50, 50, 50, 50, 50, 50, 50;
movie = 65, 60, 50, 60, 65, 50, 50, 50, 50, 50;
music = 75, 65, 50, 65, 75, 50, 50, 50, 50, 50;
sports = 42, 42, 60, 70, 70, 50, 50, 50, 50, 50;
news = 35, 40, 65, 60, 30, 50, 50, 50, 50, 50;
4k = 60, 30, 50, 60, 65, 50, 50, 50, 50, 50;
user = 50, 50, 50, 50, 50, 50, 50, 50, 50, 50;"""

    new_geq = """standard = 46, 50, 51, 48, 45, 50, 50, 50, 50, 50;
movie = 46, 50, 52, 48, 45, 50, 50, 50, 50, 50;
music = 46, 50, 50, 48, 45, 50, 50, 50, 50, 50;
sports = 46, 50, 52, 48, 45, 50, 50, 50, 50, 50;
news = 45, 50, 53, 48, 45, 50, 50, 50, 50, 50;
4k = 46, 50, 52, 48, 45, 50, 50, 50, 50, 50;
user = 50, 50, 50, 50, 50, 50, 50, 50, 50, 50;"""

    if old_geq in content:
        content = content.replace(old_geq, new_geq)

    # 2. Patch [audioamp]: disable woofer and superbass
    content = content.replace("wooferenable = 1;", "wooferenable = 0;")
    content = content.replace("woofervolume = 100;", "woofervolume = 0;")
    content = content.replace("superbass = 1;", "superbass = 0;")

    # 3. Patch [audiovolumecurve]:
    # Smooth logarithmic curve:
    # Low volumes (1-10) go down to -62 dB .. -38 dB (whisper-quiet, not blasting)
    # High volume (100) stays at 0.000 dB (no clipping)
    new_vol = "speakerVolumeGain = -65.000, -38.000, -28.000, -20.000, -15.000, -11.000, -8.000, -5.000, -3.000, -1.500, 0.000;"
    new_hp = "headPhoneVolumeGain = -65.000, -38.000, -28.000, -20.000, -15.000, -11.000, -8.000, -5.000, -3.000, -1.500, 0.000;"

    import re
    content = re.sub(r'speakerVolumeGain\s*=\s*[^;\n]+;', new_vol, content)
    content = re.sub(r'headPhoneVolumeGain\s*=\s*[^;\n]+;', new_hp, content)

    # 4. Patch [audiosws3d]: Disable SWS3D and its noisy speech expander
    content = content.replace("sws3D = 1, 0;", "sws3D = 0, 0;")
    content = content.replace("sws3D_Pregain = 1, 7;", "sws3D_Pregain = 0, 0;")
    content = content.replace("sws3D_Drc = 1, 2;", "sws3D_Drc = 0, 0;")
    content = content.replace("sws3D_Bass = 0, 5, 1, 3, 7, 5, 4;", "sws3D_Bass = 0, 0, 0, 0, 0, 0, 0;")
    content = content.replace("sws3D_Treble = 1, 60;", "sws3D_Treble = 0, 0;")
    content = content.replace("sws3D_Dialog = 1, 18, 65;", "sws3D_Dialog = 0, 0, 0;")
    content = content.replace("sws3D_Surround = 1, 20;", "sws3D_Surround = 0, 0;")
    content = content.replace("sws3D_Backgain = 0, 6;", "sws3D_Backgain = 0, 0;")
    content = content.replace("sws3D_GeqGain = 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 30, 20;", "sws3D_GeqGain = 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20;")
    content = content.replace("sws3D_Limit = 0, 19;", "sws3D_Limit = 1, 19;")

    # 5. Patch [audioconfig]: Turn off FalseAvc to stop aggressive background hiss/noise pumping
    content = content.replace("FalseAvcEnable = 1;", "FalseAvcEnable = 0;")
    content = content.replace("AvcEnable = 1;", "AvcEnable = 0;")

    # 6. Bypass SWS3D effect on Speaker to send pure clean digital PCM to DAC
    content = content.replace("Speaker = 0, 0, 0, 0, 0, 0, 30;", "Speaker = 0, 1, 0, 0, 0, 0, 30;")

    with open('/home/shrinathpol/mstar-bin-tool/aq.ini.patched', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched aq.ini with whisper-quiet low volume curve!")

if __name__ == '__main__':
    patch_aq()
