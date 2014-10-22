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

def transform(num):
    return num
    # return min(num * 30, 30000)

def cd2pngs(txtfile, con_png, dep_png):
    dept = conf = []
    import codecs
    with codecs.open(txtfile, 'r', 'utf-16') as f:
        processed = [
            [transform(int(n)) for n in line.strip().split(" ")] for line in f
        ]
        dept = processed[0]
        conf = processed[1]
    pixel2file(conf, con_png)
    pixel2file(dept, dep_png)
    
