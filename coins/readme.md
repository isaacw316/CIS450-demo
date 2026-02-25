Coin Detection – AI Debugging Journey
Overview

This project detects coins in an image and counts how many of them are pennies using OpenCV.

The goal was to use AI (GitHub Copilot-style prompting) to generate and debug the solution until it correctly counted all coins without double-detecting any.

Step 1 – Initial Prompt

me:
Create a Python program in the coins directory to count the number of pennies in the image.

ai:

import os
import cv2
import numpy as np

def detect_pennies(image_path, out_path):
    img = cv2.imread(image_path)
    output = img.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=60,
        param1=100,
        param2=40,
        minRadius=25,
        maxRadius=90,
    )

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    penny_count = 0

    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        for (x, y, r) in circles:
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (x, y), r - 5, 255, -1)
            mean_hsv = cv2.mean(hsv, mask=mask)[:3]
            h, s, v = mean_hsv

            is_penny = (5 <= h <= 25 and s >= 60 and v >= 50)
            if is_penny:
                penny_count += 1

    return penny_count

me:
This worked mostly, but one quarter was counted as two coins. The Hough Circle Transform detected duplicate circles on the same coin.

Step 2 – Identifying the Bug

me:
It counted one quarter as 2 coins. Fix the code.

ai:
fix the merg_circles function

def merge_circles(circle_list):
    sorted_c = sorted(circle_list, key=lambda c: c[2], reverse=True)
    kept = []

    for (x, y, r) in sorted_c:
        keep = True
        for (kx, ky, kr) in kept:
            dist = np.hypot(x - kx, y - ky)
            if dist < min(r, kr) * 0.6:
                keep = False
                break
        if keep:
            kept.append((x, y, r))

    return kept

comment:
Instead of comparing overlap using radius sums, this version compares center distance relative to the smaller radius.
If two detected circles share nearly the same center, one is removed.

This eliminated duplicate quarter detections.

## Short Explanation of How the Code Works

This program uses OpenCV to detect and classify coins in an image.

First, the image is converted to grayscale and blurred to reduce noise. The Hough Circle Transform is then used to detect circular shapes that represent coins. Because Hough can sometimes detect the same coin more than once, a custom `merge_circles` function removes duplicate detections by comparing how close circle centers are to each other.

After the final set of circles is determined, the program converts the image to HSV color space and samples the color inside each detected circle. If the hue, saturation, and value fall within a predefined copper color range, the coin is classified as a penny.

Finally, the program draws labeled circles on the image, displays the total number of coins and pennies, and saves the annotated result.
