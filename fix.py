# deprecated, orignally the name was wrong so use this to rename

from __future__ import print_function
from bin2png import bin2png
import sys
from os import listdir, getcwd, rename
from os.path import join
import shutil

input_dir = join(getcwd(), sys.argv[1])

for f in list(listdir(input_dir)):
    if f.endswith('.png'):
        rename(join(input_dir, f), join(input_dir, f.replace('-c.', '-d.')))
        shutil.copy2('d.png', join(input_dir, f))