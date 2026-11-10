import struct

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

def mat_mul(A, B):
    res = [0]*32
    for j in range(32):
        v = B[j]
        col = 0
        for b in range(32):
            if (v >> b) & 1:
                col ^= A[b]
        res[j] = col
    return res

def mat_vec(M, v):
    res = 0
    for b in range(32):
        if (v >> b) & 1:
            res ^= M[b]
    return res

M1 = [hisi_crc(b"\x00", 1 << b) for b in range(32)]

def shift_zeros(crc, n):
    M = M1
    res = crc
    while n > 0:
        if n & 1:
            res = mat_vec(M, res)
        M = mat_mul(M, M)
        n >>= 1
    return res

orig_bin = "/mnt/c/Users/Shri1/Downloads/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/TP.SK508.PB801-1920x1080-1G-8G-Ref69-Unionaire/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/MD_SUNNY_OVERSEA_HI3751ARBCV3510N0N_9_1_1G_STARKOS/allupgrade_V351_sos.bin"
target_bin = "/mnt/c/Users/Shri1/Downloads/PATCHED_FOR_USB/allupgrade_V351_sos.bin"

def make_key_line(hex_val, key_name):
    # Exact format: '        <key value="0x........" name="KEY_..."                   />\n'
    # Total length of 'name="KEY_..."                   />' is 35 chars before '/>'
    name_part = f'name="{key_name}"'
    assert len(name_part) <= 35
    padded = name_part.ljust(35, " ")
    line = f'        <key value="{hex_val}" {padded}/>'
    assert len(line) == 69, f"Expected 69, got {len(line)}: {line}"
    return line.encode("ascii")

key_replacements = [
    (b'        <key value="0xb8477f00" name="KEY_CHANNEL_LIST"            />', make_key_line("0xb8477f00", "KEY_ZOOMIN")),
    (b'        <key value="0xba457f00" name="KEY_RECORD"                  />', make_key_line("0xba457f00", "KEY_ZOOMOUT")),
    (b'        <key value="0xaa557f00" name="KEY_QUICK_START3"            />', make_key_line("0xaa557f00", "KEY_RED")),
    (b'        <key value="0xad527f00" name="KEY_QUICK_START4"            />', make_key_line("0xad527f00", "KEY_GREEN")),
    (b'        <key value="0xae517f00" name="KEY_QUICK_START5"            />', make_key_line("0xae517f00", "KEY_YELLOW")),
    (b'        <key value="0xaf507f00" name="KEY_QUICK_START6"            />', make_key_line("0xaf507f00", "KEY_BLUE")),
    (b'        <key value="0xe01f7f00" name="KEY_QUICK_START7"            />', make_key_line("0xe01f7f00", "KEY_IR_MOUSE")),
    (b'        <key value="0x19e67f00" name="KEY_GUIDE"                   />', make_key_line("0x19e67f00", "KEY_QUICK_START3")),
    (b'        <key value="0x0bf47f00" name="KEY_FAVORITES"               />', make_key_line("0x0bf47f00", "KEY_IR_MOUSE")),
    (b'        <key value="0x1fe07f00" name="KEY_SUBTITLE"                />', make_key_line("0x1fe07f00", "KEY_QUICK_START4")),
    (b'        <key value="0xa05f7f00" name="KEY_TIMESHIFT"               />', make_key_line("0xa05f7f00", "KEY_QUICK_START5")),
    (b'        <key value="0x18e77f00" name="KEY_TV_RADIO"                />', make_key_line("0x18e77f00", "KEY_QUICK_START6")),
]

with open(orig_bin, "rb") as fo, open(target_bin, "r+b") as ft:
    # 1. Patch /atv/etc/key.xml in Partition 16 (off=0x48a56742)
    atv_off = 0x48a56742
    fo.seek(atv_off)
    atv_sz, atv_orig_crc = struct.unpack(">II", fo.read(8))
    fo.seek(atv_off + 8 + 0x18000)
    atv_k_orig = fo.read(0x3000)
    atv_k_new = bytearray(atv_k_orig)
    for old_b, new_b in key_replacements:
        idx = atv_k_new.find(old_b)
        assert idx != -1, f"Not found in atv key.xml: {old_b}"
        atv_k_new[idx:idx+len(old_b)] = new_b
    assert len(atv_k_new) == len(atv_k_orig)

    # Compute new atv CRC via GF(2) linearity
    diff_atv = bytes(a ^ b for a, b in zip(atv_k_orig, atv_k_new))
    crc_diff_atv = shift_zeros(hisi_crc(diff_atv, 0), atv_sz - (0x18000 + len(diff_atv)))
    atv_new_crc = atv_orig_crc ^ crc_diff_atv

    ft.seek(atv_off + 4)
    ft.write(struct.pack(">I", atv_new_crc))
    ft.seek(atv_off + 8 + 0x18000)
    ft.write(atv_k_new)
    print(f"[+] Patched /atv/etc/key.xml: orig_crc=0x{atv_orig_crc:08x} -> new_crc=0x{atv_new_crc:08x}")

    # Verify full atv CRC
    ft.seek(atv_off + 8)
    atv_full_calc = hisi_crc(ft.read(atv_sz))
    assert atv_full_calc == atv_new_crc, f"ATV CRC mismatch: 0x{atv_full_calc:08x} != 0x{atv_new_crc:08x}"
    print("[+] Verified full /atv partition CRC match!")

    # 2. Patch Partition 15 (vendor, off=0x3d00365e)
    ven_off = 0x3d00365e
    fo.seek(ven_off)
    ven_sz, ven_orig_crc = struct.unpack(">II", fo.read(8))
    
    # All vendor edits lie in [0x16cd000 .. 0x19f1000]
    span_start = 0x16cd000
    span_end   = 0x19f1000
    span_len   = span_end - span_start
    fo.seek(ven_off + 8 + span_start)
    ven_span_orig = fo.read(span_len)
    ven_span_new  = bytearray(ven_span_orig)

    def replace_in_span(rel_off, length, old_sub, new_sub):
        assert len(old_sub) == len(new_sub), f"Length mismatch: {len(old_sub)} vs {len(new_sub)}"
        pos = rel_off - span_start
        chunk = ven_span_new[pos:pos+length]
        idx = chunk.find(old_sub)
        assert idx != -1, f"Not found at 0x{rel_off:x}: {old_sub[:60]}"
        ven_span_new[pos+idx : pos+idx+len(old_sub)] = new_sub

    # 2a. Patch /vendor/etc/key.xml at 0x185a000
    for old_b, new_b in key_replacements:
        replace_in_span(0x185a000, 0x3000, old_b, new_b)
    print("[+] Patched /vendor/etc/key.xml (all 54 buttons for RR pro CH.UNI-201)")

    # 2b. Patch /vendor/menu_config_xml/hotkey.xml at 0x19bb000
    old_hk = (
        b'        <HotKey single="true" type="ACTIVITY" package="com.stark.store" class="com.stark.store.ui.home.HomeActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START4</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.stark.store" class="com.stark.store.ui.myapps.MyAppsActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START6</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.android.browser" class="com.android.browser.BrowserActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START3</keycode>\n'
        b'        </HotKey>\t\t\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.hisilicon.miracast" class="com.hisilicon.miracast.activity.SettingActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START5</keycode>\n'
        b'        </HotKey>\t\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.stark.store" class="com.stark.store.ui.home.HomeActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START1</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.stark.store" class="com.stark.store.ui.myapps.MyAppsActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START2</keycode>\n'
        b'        </HotKey>'
    )
    new_hk_body = (
        b'        <HotKey single="true" type="ACTIVITY" package="com.google.android.youtube.tv" >\n'
        b'            <keycode>KEYCODE_QUICK_START1</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.netflix.mediaclient" >\n'
        b'            <keycode>KEYCODE_QUICK_START2</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.stark.store" class="com.stark.store.ui.myapps.MyAppsActivity" >\n'
        b'            <keycode>KEYCODE_QUICK_START3</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="in.startv.hotstar" >\n'
        b'            <keycode>KEYCODE_QUICK_START4</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.ecloud.eshare.server" >\n'
        b'            <keycode>KEYCODE_QUICK_START5</keycode>\n'
        b'        </HotKey>\n'
        b'        <HotKey single="true" type="ACTIVITY" package="com.amazon.avod.thirdpartyclient" >\n'
        b'            <keycode>KEYCODE_QUICK_START6</keycode>\n'
        b'        </HotKey>'
    )
    new_hk = new_hk_body.ljust(len(old_hk), b" ")
    replace_in_span(0x19bc000, 0x2000, old_hk, new_hk)
    print("[+] Patched /vendor/menu_config_xml/hotkey.xml (YouTube, Netflix, MyApps, Hotstar, EShare, Prime Video)")

    # 2c. Un-hide Google Play Store (com.android.vending) in Launcher filter at 0x19c9000 and hide com.android.traceur instead
    replace_in_span(
        0x19c9000, 0x1000,
        b'"appPackageName": "com.android.vending"',
        b'"appPackageName": "com.android.traceur"'
    )
    print("[+] Un-hid Google Play Store (com.android.vending) in Launcher & hid Traceur bloatware")

    # 2d. Patch /vendor/menu_config_xml/ro.cvte.conf at 0x19f0000
    cvte_conf_patches = [
        (b"ro.cvte.country.list=EG_GB_TH_VN_FR_MA_AE_SA", b"ro.cvte.country.list=IN_GB_TH_VN_FR_MA_AE_SA"),
        (b"persist.sys.timezone=Africa/Cairo",            b"persist.sys.timezone=Asia/Kolkata"),
        (b"ro.cvte.CVT_DEF_TIMEZONE=Africa/Cairo",        b"ro.cvte.CVT_DEF_TIMEZONE=Asia/Kolkata"),
        (b"ro.cvte.install.googleplay=0",                 b"ro.cvte.install.googleplay=1"),
        (b"ro.cvte.skip.netflix.update=0",                b"ro.cvte.skip.netflix.update=1"),
        (b"ro.cvte.CVT_EN_PREINSTALL_DEL=0",              b"ro.cvte.CVT_EN_PREINSTALL_DEL=1"),
    ]
    for old_b, new_b in cvte_conf_patches:
        replace_in_span(0x19f0000, 0x1000, old_b, new_b)
    print("[+] Patched ro.cvte.conf (Play Store enabled, Netflix update-skip, India IN, Asia/Kolkata, uninstall enabled)")

    # 2e. Patch GlobalUI / TV config at 0x19b8000
    ui_conf_patches = [
        (b"en_input_source_out_of_tv=0",                 b"en_input_source_out_of_tv=1"),
        (b"enable_global_input=0",                       b"enable_global_input=1"),
        (b"en_global_slipping_ui=0",                     b"en_global_slipping_ui=1"),
        (b"reduce_motion_level=1",                       b"reduce_motion_level=2"),
        (b"net_check_dns_default_address=www.baidu.com", b"net_check_dns_default_address=www.google.in"),
    ]
    for old_b, new_b in ui_conf_patches:
        replace_in_span(0x19b8000, 0x3000, old_b, new_b)
    print("[+] Patched GlobalUI config (IR mouse UI, global input source, fast UI animations, google.in DNS check)")

    # 2f. Patch HiRMService RAM Manager config at 0x16cd000 to block background bloatware & protect CVTE Launcher
    old_ram = (
        b'    <!-- Blacklist applications do not start by default, we will automatically start for "exception" application,\n'
        b'         and stop automatically when the application exits.\n'
        b'             The "excepted" is optional, use package name, multiple package names can be separated by ","\n'
        b'             .e.g: excepted="com.aaa.bbb,com.cccc.dddd,com.eee.ffff"\n'
        b'    -->\n\n'
        b'    <!--AppBlackList name="com.google.android.gms" />\n'
        b'    <AppBlackList name="com.android.vending" />\n'
        b'    <AppBlackList name="com.google.android.ext.services" />\n'
        b'    <AppBlackList name="com.google.android.katniss" />\n'
        b'    <AppBlackList name="com.google.android.ext.shared" />\n'
        b'    <AppBlackList name="com.google.android.gsf" />'
    )
    new_ram_body = (
        b'    <KillWhiteList name="com.cvte.tv.launcher.fall"/>\n'
        b'    <AppBlackList name="com.android.traceur"/>\n'
        b'    <AppBlackList name="com.android.soundrecorder"/>\n'
        b'    <AppBlackList name="com.android.bips"/>\n'
        b'    <AppBlackList name="com.android.printspooler"/>\n'
        b'    <AppBlackList name="com.android.simappdialog"/>\n'
        b'    <AppBlackList name="com.android.bluetoothmidiservice"/>\n'
        b'    <AppBlackList name="com.android.dreams.basic"/>'
    )
    assert len(new_ram_body) <= len(old_ram), f"new_ram_body too long: {len(new_ram_body)} > {len(old_ram)}"
    new_ram = new_ram_body.ljust(len(old_ram), b" ")
    replace_in_span(0x16cd000, 0x1000, old_ram, new_ram)
    print("[+] Patched HiRMService RAM config (blacklisted background bloatware, whitelisted Launcher)")

    # Compute new vendor CRC via GF(2) linearity
    diff_ven = bytes(a ^ b for a, b in zip(ven_span_orig, ven_span_new))
    crc_diff_ven = shift_zeros(hisi_crc(diff_ven, 0), ven_sz - span_end)
    ven_new_crc = ven_orig_crc ^ crc_diff_ven

    ft.seek(ven_off + 4)
    ft.write(struct.pack(">I", ven_new_crc))
    ft.seek(ven_off + 8 + span_start)
    ft.write(ven_span_new)
    print(f"[+] Updated vendor partition CRC: orig=0x{ven_orig_crc:08x} -> new=0x{ven_new_crc:08x}")
