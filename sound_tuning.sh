#!/system/bin/sh
# Anti-Buzzing & High-Volume Audio Clarifier for TP.SK508.PB801 (CVTE / HiSilicon Hi3751V350)
# Permanently removes "kiri kiri" screeching, plastic cabinet rattle, and digital clipping distortion

# 1. Neutralize SWS3D pre-gain (+7dB -> 0dB), DRC (+2dB -> 0dB), treble boost (+60 -> 0), surround, and band 11 (+10dB -> 0dB)
printf 'c 0\nd 0\ne 0\nf 0\nj 0\nk 0\no 0\np 0\nu 11 20\nq\n' | /vendor/bin/sample_sws3d_config > /dev/null 2>&1

# 2. Configure 5-Band Hardware Equalizer:
#    Band 0 (120 Hz):  -0.625 dB (stops speaker voice coil bottoming & plastic chassis rattle)
#    Band 1 (500 Hz):   0.000 dB (neutral mid-bass)
#    Band 2 (1500 Hz): +0.500 dB (boosts movie dialogue & voice intelligibility)
#    Band 3 (5000 Hz): -0.250 dB (removes harsh sibilance)
#    Band 4 (10000 Hz):-1.000 dB (completely silences high-frequency "kiri kiri" screeching/hiss)
printf 'n0g-625\nn1g0\nn2g500\nn3g-250\nn4g-1000\nq\n' | /vendor/bin/sample_geqconfig > /dev/null 2>&1
