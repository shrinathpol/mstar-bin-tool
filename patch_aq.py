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

    new_geq = """standard = 48, 50, 50, 50, 48, 50, 50, 50, 50, 50;
movie = 47, 50, 52, 48, 46, 50, 50, 50, 50, 50;
music = 48, 50, 50, 50, 48, 50, 50, 50, 50, 50;
sports = 48, 50, 52, 48, 46, 50, 50, 50, 50, 50;
news = 45, 50, 54, 48, 45, 50, 50, 50, 50, 50;
4k = 48, 50, 52, 48, 46, 50, 50, 50, 50, 50;
user = 50, 50, 50, 50, 50, 50, 50, 50, 50, 50;"""

    assert old_geq in content, "old_geq not found"
    content = content.replace(old_geq, new_geq)

    # 2. Patch [audioamp]: disable woofer and superbass
    content = content.replace("wooferenable = 1;", "wooferenable = 0;")
    content = content.replace("woofervolume = 100;", "woofervolume = 0;")
    content = content.replace("superbass = 1;", "superbass = 0;")

    # 3. Patch [audiovolumecurve]
    old_vol = "speakerVolumeGain = -25.000, -16.000, -13.125, -10.625, -8.500, -6.625,-4.000,-2.000, -0.125, 1.375, 3.250;"
    new_vol = "speakerVolumeGain = -25.000, -16.000, -13.125, -10.625, -8.500, -6.625, -4.000, -2.000, -1.000, -0.500, 0.000;"
    assert old_vol in content, "old_vol not found"
    content = content.replace(old_vol, new_vol)

    # Also headphone volume curve
    old_hp = "headPhoneVolumeGain = -25.000, -16.000, -13.125, -10.625, -8.500, -6.625, -4.000, -2.000, -0.125, 1.375, 3.250;"
    new_hp = "headPhoneVolumeGain = -25.000, -16.000, -13.125, -10.625, -8.500, -6.625, -4.000, -2.000, -1.000, -0.500, 0.000;"
    if old_hp in content:
        content = content.replace(old_hp, new_hp)

    # 4. Patch [audiosws3d]
    content = content.replace("sws3D_Pregain = 1, 7;", "sws3D_Pregain = 0, 0;")
    content = content.replace("sws3D_Drc = 1, 2;", "sws3D_Drc = 0, 0;")
    content = content.replace("sws3D_Bass = 0, 5, 1, 3, 7, 5, 4;", "sws3D_Bass = 0, 0, 0, 0, 0, 0, 0;")
    content = content.replace("sws3D_Treble = 1, 60;", "sws3D_Treble = 0, 0;")
    content = content.replace("sws3D_Dialog = 1, 18, 65;", "sws3D_Dialog = 1, 10, 50;")
    content = content.replace("sws3D_Surround = 1, 20;", "sws3D_Surround = 0, 0;")
    content = content.replace("sws3D_Backgain = 0, 6;", "sws3D_Backgain = 0, 0;")
    content = content.replace("sws3D_GeqGain = 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 30, 20;", "sws3D_GeqGain = 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20;")
    content = content.replace("sws3D_Limit = 0, 19;", "sws3D_Limit = 1, 19;")

    with open('/home/shrinathpol/mstar-bin-tool/aq.ini.patched', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched all sections in aq.ini!")

if __name__ == '__main__':
    patch_aq()
