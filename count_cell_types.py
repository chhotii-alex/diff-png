#!/usr/bin/python3

import os
import re
import skimage
import numpy as np
from collections import defaultdict
import sys
from matplotlib import pyplot as plt
#from termcolor import colored, cprint

# flatten pixel dimensions
def flatten(img):
    return img.reshape(img.shape[0]*img.shape[1], *img.shape[2:])

# put unique colors with counts  into dictionary
# Return value: dictionary such that:
# key -- tuple representing a color (r, g, b, alpha)
# value -- number of pixels with that color
def count_colors(img):
    colors, counts = np.unique(img, axis=0, return_counts=True) # Get unique colors with counts
    count_dict = {k: v for k,v in zip([tuple(x) for x in colors], [x for x in counts])} # put unique colors with counts into dictionary
    d = defaultdict(int) # transfer to a dict that will respond 0 for missing things
    d.update(count_dict)
    return d

def get_counts_for_color_names(count_dict, name_to_rgb):
    return {name: count_dict[rgb] for name, rgb in name_to_rgb.items()}

def count_pixels(path, show_cut=False, include_red=True):
    img = np.array(skimage.io.imread(path)) # read the image and covert to numpy array
    border = 21
    img = img[:-border+1, border:,:] # Cut out border with axes
    img2 = img[:-25,:,:] # Cut out 'ghosts', only used for blue counts
    if show_cut:
        plt.imshow(img2)
        plt.show()
    img =  flatten(img)
    img2 = flatten(img2)
    inside_axes_counts = count_colors(img)
    ghost_clipped_counts = count_colors(img2)

    # Do non-blue colors for all area inside axes
    name_to_rgb = {
	'green': (0,128,0,255),
	'bright green': (0,255,0,255),
	'cyan': (0,128,128,255),
	'bright cyan':  (0,255,255,255),
	'purple': (128,0,128,255),
	'bright purple': (255,0,255,255),
    }
    if include_red:
        name_to_rgb.update({
            'red': (128, 0, 0, 255),
            'bright red': (255, 0, 0, 255),  # I am guessing on the color values for this one
        })
    return_dict = get_counts_for_color_names(inside_axes_counts, name_to_rgb)
    # Do blue counts with ghost area clipped off
    blue_colors = {
	'blue': (0,0,128,255),
	'bright blue': (0,0,255,255),
    }
    return_dict.update(get_counts_for_color_names(ghost_clipped_counts, blue_colors))
    return return_dict

color_code = {
        'purple' : 'LYMPH',
        'blue' : 'IG',
        'green' : 'MONO',
        'cyan' : 'NEUT',
        'red' : 'EO',
    }

def scaling_for_name(color_name, scale_factor):
    if 'bright' in color_name:
        return scale_factor
    else:
        return 1
    
def is_cell_type(color_name, cell_type):
    color_name = color_name.split(" ")[-1]
    if color_code[color_name] == cell_type:
        return 1
    else:
        return 0

def print_pixel_counts(color_counts):
    total_count = np.sum([v for k, v in color_counts.items()])
    for k,v in color_counts.items():
        perc = np.round(v/total_count, 2)
        print(f"{k}: {v} ({perc*100}%)")
    print()
    print("Total colored pixel count: %d" % total_count)

def calc_percent_lymph(color_counts, scale_factor):
    total_weight = np.sum([v*scaling_for_name(k, scale_factor) for k, v in color_counts.items()])
    lymph = np.sum([v*scaling_for_name(k, scale_factor)*is_cell_type(k, "LYMPH") for k, v in color_counts.items()])
    lymph_frac = lymph / total_weight
    return np.round(lymph_frac*100)

def calc_area_lymph(color_counts, scale_factor):
    return calc_area("LYMPH", color_counts, scale_factor)

def calc_area(cell_type, color_counts, scale_factor):
    return np.sum([v*scaling_for_name(k, scale_factor)*is_cell_type(k, cell_type) for k, v in color_counts.items()])

filename_pattern = re.compile(r"XN.*\(Build 164\)_\d\d\d\d\d\d\d\d_\d\d\d\d\d\d_(.*)_WDF.png")
def extract_sample_id(filename):
    m = filename_pattern.match(filename)
    if m:
        return m.group(1)
    else:
        return None

if __name__ == '__main__':
    cell_types = ["NEUT", "LYMPH", "MONO", "EO", "BASO", "IG"]
    print("\t".join(["ID       "] + cell_types))
    if len(sys.argv) < 2:
        directory = "."
    else:
        directory = sys.argv[1]
    directory_encoded = os.fsencode(directory)
    for file in os.listdir(directory_encoded):
        filename = os.fsdecode(file)
        if not filename.endswith("_WDF.png"):
            continue
        sample_id = extract_sample_id(filename)
        if sample_id is None:
            sample_id = "Could not parse out sample ID from filename: " + filename
        filepath = os.path.join(directory, filename)
        counts = count_pixels(filepath)
        #percent_lymph = calc_percent_lymph(counts, 2)
        areas = [calc_area(ct, counts, 2) for ct in cell_types]
        print("\t".join([sample_id] + [str(a) for a in areas]))
        #print(int(percent_lymph), round(100*calc_area("LYMPH", counts, 2)/np.sum(areas)))

