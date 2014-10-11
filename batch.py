from __future__ import print_function
from bin2png import bin2png
import sys
from os import listdir, getcwd
from os.path import join

if len(sys.argv) < 2:
    print("pass in input and output folders")

input_dir = join(getcwd(), sys.argv[1])
output_dir = join(getcwd(), sys.argv[2])

for f in listdir(input_dir):
    if f.endswith('.bin'):
        bin2png(join(input_dir, f), join(output_dir, 'default-' + str(int(f.split('_')[0])) + '-d.png'))