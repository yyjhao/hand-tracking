from __future__ import print_function
import struct
import png

cols = 320
rows = 240

size = rows * cols

def gen_c():
    def transform(pix):
        # whack
        if pix < 0.1:
            return 32001
        else:
            return pix

    pixels = [
        [700 for c in xrange(cols)]
        for r in xrange(rows)
    ]

    p = png.from_array(pixels, 'L', {'bitdepth': 16})
    p.save('d.png')
