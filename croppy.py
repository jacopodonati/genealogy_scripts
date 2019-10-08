import os, sys, glob
from PIL import Image

print('Deleting old crops...')
import os, glob
for filename in glob.glob('./crop_*'):
    os.remove(filename)

print('Cropping...')
prefix = 'crop_'
first = 4
last = 509
zfill = 3
width = 1050
height = 800
l_margin = 570
t_margin = 600
r_margin = 570
is_left = True

for i in range(first, last + 1):
    current_file = str(i).zfill(zfill) + '.jpg'
    im = Image.open(current_file)
    if is_left:
        left = l_margin
        top = t_margin
        right = l_margin + width
        bottom = t_margin + height
    else:
        left = im.size[0] - r_margin - width
        top = t_margin
        right = im.size[0] - r_margin
        bottom = t_margin + height
    is_left = not is_left
    new_im = im.crop((left, top, right, bottom))
    new_im.save(prefix + current_file)

print('Done.')
