import os
import cv2
import numpy as np


def merge_circles(circle_list):
    """
    Remove duplicate detections by comparing center distance.
    Keeps the larger circle if two are nearly the same coin.
    """
    sorted_c = sorted(circle_list, key=lambda c: c[2], reverse=True)
    kept = []

    for (x, y, r) in sorted_c:
        keep = True

        for (kx, ky, kr) in kept:
            dist = np.hypot(x - kx, y - ky)

            # If centers are very close, it's the same coin
            if dist < min(r, kr) * 0.6:
                keep = False
                break

        if keep:
            kept.append((x, y, r))

    return kept


def detect_pennies(image_path, out_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    output = img.copy()

    # Convert to grayscale and blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    # Hough Circle Detection
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=80,        # Increased to prevent close duplicates
        param1=100,
        param2=40,
        minRadius=25,
        maxRadius=90,
    )

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    detected = []
    penny_count = 0

    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        circle_list = [(int(x), int(y), int(r)) for (x, y, r) in circles]

        merged = merge_circles(circle_list)

        for i, (x, y, r) in enumerate(merged, start=1):

            # Create mask inside circle for accurate color sampling
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (x, y), r - 5, 255, -1)

            mean_hsv = cv2.mean(hsv, mask=mask)[:3]
            h, s, v = mean_hsv

            # Penny color range (copper/orange)
            is_penny = (
                5 <= h <= 25 and
                s >= 60 and
                v >= 50
            )

            if is_penny:
                penny_count += 1

            color = (0, 0, 255) if is_penny else (255, 0, 0)

            # Draw circle and label
            cv2.circle(output, (x, y), r, color, 2)
            cv2.circle(output, (x, y), 2, (0, 255, 0), 3)
            cv2.putText(
                output,
                str(i),
                (x - 10, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            detected.append((x, y, r, is_penny))

    total_coins = len(detected)

    # Annotate totals
    cv2.putText(output, f"Total Coins: {total_coins}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(output, f"Pennies: {penny_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.imwrite(out_path, output)

    return total_coins, penny_count


def main():
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, "coins.png")
    output_path = os.path.join(script_dir, "coins_detected.png")

    total, pennies = detect_pennies(image_path, output_path)

    print(f"Total coins detected: {total}")
    print(f"Pennies counted: {pennies}")
    print(f"Annotated image saved to: {output_path}")


if __name__ == "__main__":
    main()