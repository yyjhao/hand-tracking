from __future__ import print_function
import struct
import png

cols = 320
rows = 240

size = rows * cols

def pixel2file(one_row, png_file):
    pixels = [
        [one_row[r * cols + c] for c in xrange(cols)]
        for r in xrange(rows)
    ]

    p = png.from_array(pixels, 'L', {'bitdepth': 16})
    p.save(png_file)

def fixshit(s):
    return s
    if len(s) == 1:
        return '0' + s
    else:
        return s


def file_to_pngs(txtfile, prefix):
    num = 0
    is_c = False
    import codecs
    with codecs.open(txtfile, 'r', 'utf-16') as f:
        for line in f:
            pixels = [int(n) for n in line.strip().split(" ")]
            if is_c:
                pixel2file(pixels, prefix + "-" + fixshit(str(num)) + "-c.png")
                is_c = False
                num += 1
            else:
                pixel2file(pixels, prefix + "-" + fixshit(str(num)) + "-d.png")
                is_c = True

    
