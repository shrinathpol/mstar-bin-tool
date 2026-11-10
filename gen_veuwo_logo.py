import math, struct, time

t0 = time.time()
with open("/tmp/orig_logo.jpg", "rb") as f:
    orig = f.read()

# Extract exact header up to end of SOS (0x269f + 2 + 12 = 0x26ad)
header = orig[:0x26ad]

# Parse DQT0 and DQT1 from orig (at 0x245c)
dqt0 = list(orig[0x245c+5 : 0x245c+5+64])
dqt1 = list(orig[0x245c+70 : 0x245c+70+64])

# Parse DHT tables from orig (at 0x24fb + 4 .. 0x269f)
dht_data = orig[0x24fb+4 : 0x269f]
huff_tables = {}
pos = 0
while pos < len(dht_data):
    tc_th = dht_data[pos]
    pos += 1
    counts = list(dht_data[pos:pos+16])
    pos += 16
    table = {}
    code = 0
    for bits in range(1, 17):
        for _ in range(counts[bits-1]):
            sym = dht_data[pos]
            pos += 1
            table[sym] = (code, bits)
            code += 1
        code <<= 1
    huff_tables[tc_th] = table

dc0_tab = huff_tables[0x00]
ac0_tab = huff_tables[0x10]
dc1_tab = huff_tables[0x01]
ac1_tab = huff_tables[0x11]

ZIGZAG = [
     0,  1,  5,  6, 14, 15, 27, 28,
     2,  4,  7, 13, 16, 26, 29, 42,
     3,  8, 12, 17, 25, 30, 41, 43,
     9, 11, 18, 24, 31, 40, 44, 53,
    10, 19, 23, 32, 39, 45, 52, 54,
    20, 22, 33, 38, 46, 51, 55, 60,
    21, 34, 37, 47, 50, 56, 59, 61,
    35, 36, 48, 49, 57, 58, 62, 63
]

# Precompute 1D DCT matrix C[u][x] = alpha(u) * cos((2x+1)*u*pi/16)
C = [[0.0]*8 for _ in range(8)]
for u in range(8):
    a = math.sqrt(1.0/8.0) if u == 0 else math.sqrt(2.0/8.0)
    for x in range(8):
        C[u][x] = a * math.cos((2*x + 1) * u * math.pi / 16.0)

def dct_quant_8x8(block, qtab):
    # block is 64 floats (level-shifted by -128)
    # 1D DCT along rows
    tmp = [0.0]*64
    for i in range(8):
        row = block[i*8:(i+1)*8]
        for u in range(8):
            cu = C[u]
            tmp[i*8 + u] = (cu[0]*row[0] + cu[1]*row[1] + cu[2]*row[2] + cu[3]*row[3] +
                            cu[4]*row[4] + cu[5]*row[5] + cu[6]*row[6] + cu[7]*row[7])
    # 1D DCT along cols + zigzag + quantize
    out = [0]*64
    for v in range(8):
        cv = C[v]
        for u in range(8):
            val = (cv[0]*tmp[0*8+u] + cv[1]*tmp[1*8+u] + cv[2]*tmp[2*8+u] + cv[3]*tmp[3*8+u] +
                   cv[4]*tmp[4*8+u] + cv[5]*tmp[5*8+u] + cv[6]*tmp[6*8+u] + cv[7]*tmp[7*8+u])
            z = ZIGZAG[v*8 + u]
            out[z] = int(round(val / qtab[z]))
    return out

# Signed Distance Field (SDF) helper functions for crisp anti-aliased vector rendering of "veuwo"
def sd_segment(px, py, ax, ay, bx, by):
    pax, pay = px - ax, py - ay
    bax, bay = bx - ax, by - ay
    h = max(0.0, min(1.0, (pax*bax + pay*bay) / (bax*bax + bay*bay)))
    dx, dy = pax - bax*h, pay - bay*h
    return math.hypot(dx, dy)

# Render "veuwo" wordmark matching the TV bezel logo in a bounding box:
# Center = (960, 520), total width ~ 880 px, height ~ 180 px
# Let's define each letter ("v", "e", "u", "w", "o") with clean geometric SDF strokes!
stroke_r = 21.0  # half-stroke thickness = 21px (total stroke width = 42px)

def letter_v(px, py, cx, cy):
    # V: top-left (-68, -68) -> bottom (0, 68) -> top-right (68, -68)
    d1 = sd_segment(px, py, cx - 64, cy - 64, cx, cy + 64)
    d2 = sd_segment(px, py, cx, cy + 64, cx + 64, cy - 64)
    return min(d1, d2) - stroke_r

def letter_e(px, py, cx, cy):
    # Geometric rounded 'e' matching exact 64px centerline height of v, u, w, o
    dx, dy = px - cx, py - cy
    R = 64.0
    r = math.hypot(dx, dy)
    a_deg = math.degrees(math.atan2(dy, dx))
    if 2.0 < a_deg < 42.0:
        a1, a2 = math.radians(2.0), math.radians(42.0)
        d_ring = min(math.hypot(dx - R*math.cos(a1), dy - R*math.sin(a1)),
                     math.hypot(dx - R*math.cos(a2), dy - R*math.sin(a2))) - stroke_r
    else:
        d_ring = abs(r - R) - stroke_r
    d_bar = sd_segment(px, py, cx - 60, cy + 1, cx + R, cy + 1) - (stroke_r * 0.88)
    return min(d_ring, d_bar)

def letter_u(px, py, cx, cy):
    dx, dy = px - cx, py - (cy + 8)
    if dy < 0:
        d1 = sd_segment(px, py, cx - 56, cy - 64, cx - 56, cy + 8)
        d2 = sd_segment(px, py, cx + 56, cy - 64, cx + 56, cy + 8)
        return min(d1, d2) - stroke_r
    else:
        return abs(math.hypot(dx, dy) - 56.0) - stroke_r

def letter_w(px, py, cx, cy):
    d1 = sd_segment(px, py, cx - 94, cy - 64, cx - 47, cy + 64)
    d2 = sd_segment(px, py, cx - 47, cy + 64, cx, cy - 34)
    d3 = sd_segment(px, py, cx, cy - 34, cx + 47, cy + 64)
    d4 = sd_segment(px, py, cx + 47, cy + 64, cx + 94, cy - 64)
    return min(d1, d2, d3, d4) - stroke_r

def letter_o(px, py, cx, cy):
    return abs(math.hypot(px - cx, py - cy) - 64.0) - stroke_r

def logo_sdf(px, py):
    cy = 515.0
    d = min(
        letter_v(px, py, 565.0, cy),
        letter_e(px, py, 745.0, cy),
        letter_u(px, py, 930.0, cy),
        letter_w(px, py, 1145.0, cy),
        letter_o(px, py, 1365.0, cy),
    )
    return d

def rgb_to_ycbcr(r, g, b):
    y  =  0.299*r + 0.587*g + 0.114*b
    cb = -0.168736*r - 0.331264*g + 0.5*b + 128.0
    cr =  0.5*r - 0.418688*g - 0.081312*b + 128.0
    return y - 128.0, cb - 128.0, cr - 128.0

# Background color: clean white (255, 255, 255) or sleek dark?
# Wait: let's check both or make a sleek dark navy/black background with crisp white "veuwo" and a subtle blue accent bar underneath!
bg_y, bg_cb, bg_cr = rgb_to_ycbcr(10, 14, 22)
bg_block_y  = dct_quant_8x8([bg_y]*64, dqt0)
bg_block_cb = dct_quant_8x8([bg_cb]*64, dqt1)
bg_block_cr = dct_quant_8x8([bg_cr]*64, dqt1)

def encode_number(val):
    if val == 0:
        return 0, 0
    aval = abs(val)
    bits = aval.bit_length()
    code = val if val > 0 else (val - 1) & ((1 << bits) - 1)
    return bits, code

class BitWriter:
    def __init__(self):
        self.out = bytearray()
        self.buf = 0
        self.nbits = 0

    def put_bits(self, code, n):
        self.buf = (self.buf << n) | code
        self.nbits += n
        while self.nbits >= 8:
            self.nbits -= 8
            b = (self.buf >> self.nbits) & 0xff
            self.out.append(b)
            if b == 0xff:
                self.out.append(0x00)

    def flush_rst(self, rst_idx):
        if self.nbits > 0:
            pad = (1 << (8 - self.nbits)) - 1
            self.put_bits(pad, 8 - self.nbits)
        self.nbits = 0
        self.buf = 0
        self.out.append(0xff)
        self.out.append(0xd0 + (rst_idx & 7))

    def finish(self):
        if self.nbits > 0:
            pad = (1 << (8 - self.nbits)) - 1
            self.put_bits(pad, 8 - self.nbits)
        self.out.append(0xff)
        self.out.append(0xd9)

def encode_block(bw, zz, prev_dc, dc_tab, ac_tab):
    diff = zz[0] - prev_dc
    s, c = encode_number(diff)
    hc, hb = dc_tab[s]
    bw.put_bits(hc, hb)
    if s > 0:
        bw.put_bits(c, s)
    # AC
    last_nz = 0
    for k in range(63, 0, -1):
        if zz[k] != 0:
            last_nz = k
            break
    if last_nz == 0:
        hc, hb = ac_tab[0x00]
        bw.put_bits(hc, hb)
        return zz[0]
    zero_run = 0
    for k in range(1, last_nz + 1):
        v = zz[k]
        if v == 0:
            zero_run += 1
        else:
            while zero_run >= 16:
                hc, hb = ac_tab[0xf0]
                bw.put_bits(hc, hb)
                zero_run -= 16
            s, c = encode_number(v)
            sym = (zero_run << 4) | s
            hc, hb = ac_tab[sym]
            bw.put_bits(hc, hb)
            bw.put_bits(c, s)
            zero_run = 0
    if last_nz < 63:
        hc, hb = ac_tab[0x00]
        bw.put_bits(hc, hb)
    return zz[0]

bw = BitWriter()
rst_idx = 0

# Active logo bounding box in 8x8 blocks:
# x: 500..1420 -> bx: 60..180
# y: 420..650  -> by: 52..82
for by in range(135):
    pred_y = pred_cb = pred_cr = 0
    in_y_box = (50 <= by <= 82)
    for bx in range(240):
        if in_y_box and (58 <= bx <= 184):
            blk_y, blk_cb, blk_cr = [], [], []
            x0, y0 = bx * 8, by * 8
            for py in range(y0, y0 + 8):
                for px in range(x0, x0 + 8):
                    d = logo_sdf(px, py)
                    # Also subtle blue-cyan accent line under logo at y=632..638, x=720..1200
                    d_bar = max(abs(px - 960.0) - 180.0, abs(py - 634.0) - 2.5)
                    # Smooth anti-aliasing over 1.5px
                    alpha_logo = max(0.0, min(1.0, 0.5 - d / 1.6))
                    alpha_bar  = max(0.0, min(1.0, 0.5 - d_bar / 1.5))
                    r = 10.0 + 245.0 * alpha_logo + 20.0 * alpha_bar
                    g = 14.0 + 241.0 * alpha_logo + 165.0 * alpha_bar
                    b = 22.0 + 233.0 * alpha_logo + 240.0 * alpha_bar
                    r, g, b = min(255.0, r), min(255.0, g), min(255.0, b)
                    yy, cb, cr = rgb_to_ycbcr(r, g, b)
                    blk_y.append(yy)
                    blk_cb.append(cb)
                    blk_cr.append(cr)
            zy  = dct_quant_8x8(blk_y, dqt0)
            zcb = dct_quant_8x8(blk_cb, dqt1)
            zcr = dct_quant_8x8(blk_cr, dqt1)
        else:
            zy, zcb, zcr = bg_block_y, bg_block_cb, bg_block_cr
        pred_y  = encode_block(bw, zy,  pred_y,  dc0_tab, ac0_tab)
        pred_cb = encode_block(bw, zcb, pred_cb, dc1_tab, ac1_tab)
        pred_cr = encode_block(bw, zcr, pred_cr, dc1_tab, ac1_tab)
    if by < 134:
        bw.flush_rst(rst_idx)
        rst_idx += 1

bw.finish()
jpg_bytes = header + bytes(bw.out)
out_path = "/home/shrinathpol/.gemini/antigravity/brain/d0e5ab4e-a107-4aad-8672-0ad5bfcde781/veuwo_logo.jpg"
with open(out_path, "wb") as f:
    f.write(jpg_bytes)
print(f"Generated {out_path}: {len(jpg_bytes)} bytes (0x{len(jpg_bytes):x}) in {time.time()-t0:.2f}s")
