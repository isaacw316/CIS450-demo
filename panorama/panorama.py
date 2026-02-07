#!/usr/bin/env python

"""
Stitching sample
================

Simple panorama stitching using OpenCV's Stitcher API.
"""

from __future__ import print_function

import cv2 as cv
import argparse
import sys

# Stitching modes
modes = (cv.Stitcher_PANORAMA, cv.Stitcher_SCANS)

# Argument parser
parser = argparse.ArgumentParser(
    prog='panorama.py',
    description='Stitch images into a panorama'
)

parser.add_argument(
    '--mode',
    type=int,
    choices=modes,
    default=cv.Stitcher_PANORAMA,
    help=(
        'Stitcher mode. PANORAMA (0) for photos, '
        'SCANS (1) for scans.'
    )
)

parser.add_argument(
    '--output',
    default='result.jpg',
    help='Output image filename (default: result.jpg)'
)

parser.add_argument(
    'img',
    nargs='+',
    help='Input image files'
)


def main():
    args = parser.parse_args()

    # Read input images
    imgs = []
    for img_name in args.img:
        img = cv.imread(img_name)
        if img is None:
            print("Can't read image:", img_name)
            sys.exit(1)
        imgs.append(img)

    print(f"Loaded {len(imgs)} images")

    # Create stitcher
    stitcher = cv.Stitcher.create(args.mode)

    status, pano = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code =", status)
        sys.exit(1)

    # Save result
    cv.imwrite(args.output, pano)
    print("Stitching completed successfully!")
    print("Saved as:", args.output)


if __name__ == '__main__':
    main()
