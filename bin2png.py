from __future__ import print_function
import struct
import png

cols = 320
rows = 240

size = rows * cols

def bin2png(bin_file, png_file):
    with open(bin_file, "rb") as f:
        nums = struct.unpack('f' * size, f.read(size * 4))

    def transform(pix):
        # whack
        if pix < 0.1:
            return 32001
        else:
            return pix

    pixels = [
        [transform(nums[r * cols + c]) for c in xrange(cols)]
        for r in xrange(rows)
    ]

    p = png.from_array(pixels, 'L', {'bitdepth': 16})
    p.save(png_file)
