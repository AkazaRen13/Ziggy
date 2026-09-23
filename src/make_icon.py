import struct, zlib, os

def png_chunk(name, data):
    c = zlib.crc32(name + data) & 0xffffffff
    return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

def make_png(size, bg, accent, accent_light):
    def hex2rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2],16) for i in (0,2,4))
    bg_r = hex2rgb(bg)
    ac_r = hex2rgb(accent)
    al_r = hex2rgb(accent_light)

    pixels = []
    cx = cy = size // 2
    r = size // 2 - 2

    for y in range(size):
        row = []
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            # border ring
            if r - 3 <= dist <= r:
                row += list(ac_r) + [255]
            elif dist < r - 3:
                # left eye
                ex1, ey1, er1 = size*18//72, size*24//72, size*5//72
                # right eye
                ex2, ey2, er2 = size*43//72, size*24//72, size*5//72
                in_eye1 = ((x-ex1)**2 + (y-ey1)**2) < er1**2
                in_eye2 = ((x-ex2)**2 + (y-ey2)**2) < er2**2
                # shine
                shine1 = ((x-(ex1-2))**2 + (y-(ey1-2))**2) < (er1//3)**2
                shine2 = ((x-(ex2-2))**2 + (y-(ey2-2))**2) < (er2//3)**2
                if shine1 or shine2:
                    row += [255,255,255,255]
                elif in_eye1 or in_eye2:
                    row += list(al_r) + [255]
                else:
                    row += list(bg_r) + [255]
            else:
                row += [0,0,0,0]
        pixels.append(bytes(row))

    raw = b''.join(b'\x00' + row for row in pixels)
    compressed = zlib.compress(raw)

    png = b'\x89PNG\r\n\x1a\n'
    png += png_chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    png += png_chunk(b'IDAT', compressed)
    png += png_chunk(b'IEND', b'')
    return png

def make_ico(path):
    sizes = [256, 128, 64, 32, 16]
    pngs = [make_png(s, "#1a1a2e", "#7c6ee6", "#a99cf0") for s in sizes]

    n = len(sizes)
    header = struct.pack('<HHH', 0, 1, n)
    offset = 6 + n * 16
    directory = b''
    for i, (s, png) in enumerate(zip(sizes, pngs)):
        sz = s if s < 256 else 0
        directory += struct.pack('<BBBBHHII', sz, sz, 0, 0, 1, 32, len(png), offset)
        offset += len(png)

    with open(path, 'wb') as f:
        f.write(header + directory + b''.join(pngs))
    print(f"Saved: {path}")

make_ico(os.path.join(os.path.dirname(__file__), "ziggy.ico"))