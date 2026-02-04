import cv2 as cv
import os
import sys

photos_dir = r"C:\Users\ikecr\OneDrive\Desktop\CIS450\CIS450-demo\photos\Photos"
output_dir = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(photos_dir):

    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    img_path = os.path.join(photos_dir, filename)
    img = cv.imread(img_path)

    if img is None:
        print(f"Could not read {filename}")
        continue

    original_height, original_width = img.shape[:2]

    new_width = 640
    scale_ratio = new_width / original_width
    new_height = round(original_height * scale_ratio)

    resized = cv.resize(
        img,
        (new_width, new_height),
        interpolation=cv.INTER_LINEAR
    )

    name, _ = os.path.splitext(filename)
    new_filename = f"{name}-640x{new_height}.png"
    output_path = os.path.join(output_dir, new_filename)

    cv.imwrite(output_path, resized)
    print(f"Saved {new_filename}")
