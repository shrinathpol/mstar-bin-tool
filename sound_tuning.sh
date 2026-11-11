#!/system/bin/sh
# Anti-Noise, Anti-Hiss & Low-Volume Softener for TP.SK508.PB801 (HiSilicon Hi3751V350)
# Calibrated for gentle, whisper-quiet low volumes (Volume 1-5) and distortion-free dialogue

# 1. Disable Auto Volume Control (AVC) to stop background noise/hiss floor pumping
printf 'd\nq\n' | /vendor/bin/sample_avc_config > /dev/null 2>&1

# 2. Disable SWS3D audio effect and speech expansion harmonics (stops frying/sizzling on dialogue)
printf 'a 0\nc 0\nd 0\ne 0\nf 0\nj 0\nk 0\nl 0\nm 0\nn 0\no 0\np 0\nu 11 20\nq\n' | /vendor/bin/sample_sws3d_config > /dev/null 2>&1

# 3. Apply calibrated 5-Band Hardware Equalizer:
#    - Attenuates baseline level by ~8 dB so Volume 1-5 is soft and whisper-quiet instead of blasting.
#    - Retains speech intelligibility at 1500 Hz while keeping 120 Hz and 10000 Hz rattle-free.
#    Band 0 (120 Hz):  -8.000 dB (eliminates bass over-excursion & plastic back cover buzz)
#    Band 1 (500 Hz):  -8.000 dB (clean warm body)
#    Band 2 (1500 Hz): -7.500 dB (+0.5 dB relative boost for dialogue clarity)
#    Band 3 (5000 Hz): -8.000 dB (smooth high-mids)
#    Band 4 (10000 Hz):-9.000 dB (silences hiss and harsh sibilant sizzle)
printf 'n0g-8000\nn1g-8000\nn2g-7500\nn3g-8000\nn4g-9000\nq\n' | /vendor/bin/sample_geqconfig > /dev/null 2>&1
