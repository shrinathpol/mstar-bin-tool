#!/system/bin/sh
# Anti-Noise, Anti-Hiss & Anti-Vibration Clarifier for TP.SK508.PB801 (HiSilicon Hi3751V350)
# Permanently silences background hiss, speech pumping noise, plastic rattle, and sibilant screeching

# 1. Disable Auto Volume Control (AVC) to stop background noise/hiss floor pumping
printf 'd\nq\n' | /vendor/bin/sample_avc_config > /dev/null 2>&1

# 2. Disable SWS3D audio effect and speech expansion harmonics (stops frying/sizzling on dialogue)
printf 'a 0\nc 0\nd 0\ne 0\nf 0\nj 0\nk 0\nl 0\nm 0\nn 0\no 0\np 0\nu 11 20\nq\n' | /vendor/bin/sample_sws3d_config > /dev/null 2>&1

# 3. Apply calibrated 5-Band Hardware Equalizer:
#    Band 0 (120 Hz):  -1.250 dB (eliminates bass over-excursion & plastic back cover buzz)
#    Band 1 (500 Hz):   0.000 dB (natural mid-body)
#    Band 2 (1500 Hz): +0.625 dB (crystal clear vocal clarity for Kannada dialogue)
#    Band 3 (5000 Hz): -0.500 dB (eliminates sharp harshness)
#    Band 4 (10000 Hz):-1.500 dB (cuts off high-frequency hiss, static noise, and sibilant sizzle)
printf 'n0g-1250\nn1g0\nn2g625\nn3g-500\nn4g-1500\nq\n' | /vendor/bin/sample_geqconfig > /dev/null 2>&1
