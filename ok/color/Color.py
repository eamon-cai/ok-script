import os
from collections import defaultdict

import cv2
import numpy as np

from ok.feature.Box import Box

black_color = {
    'r': (0, 0),  # Red range
    'g': (0, 0),  # Green range
    'b': (0, 0)  # Blue range
}

white_color = {
    'r': (255, 255),  # Red range
    'g': (255, 255),  # Green range
    'b': (255, 255)  # Blue range
}


def is_close_to_pure_color(image, max_colors=5000, percent=0.97):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Step 2: Initialize a dictionary to count color frequencies
    color_counts = defaultdict(int)
    # Step 3: Go through each pixel and count
    for row in image:
        for pixel in row:
            # Convert the pixel tuple to a hashable type for counting
            color = tuple(pixel)
            color_counts[color] += 1
            if len(color_counts) > max_colors:
                return False

    # Step 4: Find the most dominant color and its percentage
    dominant_color = max(color_counts, key=color_counts.get)
    dominant_count = color_counts[dominant_color]
    total_pixels = image.shape[0] * image.shape[1]
    percentage = (dominant_count / total_pixels)

    return percentage > percent


def calculate_colorfulness(image, box=None):
    if box is not None:
        image = image[box.y:box.y + box.height, box.x:box.x + box.width, :3]
    # Split the image into its respective RGB components
    (B, G, R) = cv2.split(image.astype("float"))

    # Compute rg = R - G
    rg = np.absolute(R - G)

    # Compute yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)

    # Compute the mean and standard deviation of both rg and yb
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))

    # Combine the mean and standard deviation
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))

    # Derive the "colorfulness" metric
    colorfulness = stdRoot + (0.3 * meanRoot)

    return colorfulness / 100


def get_saturation(image, box=None):
    # Load the image

    # Check if image loaded successfully
    if image is None:
        raise ValueError("Image not found or path is incorrect")

    if box is not None:
        if (box.x >= 0 and box.y >= 0 and
            box.x + box.width <= image.shape[1] and  # image.shape[1] is the width of the image
            box.y + box.height <= image.shape[
                0]) and box.width > 0 and box.height > 0:  # image.shape[0] is the height of the image

            # Extract the region of interest (ROI) using slicing

            image = image[box.y:box.y + box.height, box.x:box.x + box.width, :3]

    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Extract the saturation channel
    saturation_channel = hsv_image[:, :, 1]

    # Calculate the mean saturation
    mean_saturation = saturation_channel.mean() / 255

    # If the mean saturation is above the threshold, the image is colored; otherwise, it is grayscale
    return mean_saturation


def find_color_rectangles(image, color_range, min_width, min_height, max_width=-1, max_height=-1, threshold=0.95,
                          box=None):
    if image is None:
        raise ValueError("Image not found or path is incorrect")
    if box is not None:
        image = image[box.y:box.y + box.height, box.x:box.x + box.width, :3]
        x_offset = box.x
        y_offset = box.y
    else:
        x_offset = 0
        y_offset = 0

    # Convert color range to BGR format for OpenCV
    lower_bound = np.array([color_range['b'][0], color_range['g'][0], color_range['r'][0]], dtype="uint8")
    upper_bound = np.array([color_range['b'][1], color_range['g'][1], color_range['r'][1]], dtype="uint8")

    # Create a mask for the color range
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    results = []

    for contour in contours:
        # Get the bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        # Check if the rectangle meets the size criteria
        if w >= min_width and h >= min_height and (max_height == -1 or h <= max_height) and (
                max_width == -1 or w <= max_width):

            # Extract the region of interest (ROI) from the mask
            roi_mask = mask[y:y + h, x:x + w]

            # Calculate the total number of pixels in the ROI
            total_pixels = roi_mask.size

            # Calculate the number of matching pixels (value 255)
            matching_pixels = np.sum(roi_mask == 255)

            # Check if the percentage of matching pixels is greater than or equal to 90%\
            percent = (matching_pixels / total_pixels)
            if percent >= threshold:
                # Store the result
                results.append(
                    Box(x + x_offset, y + y_offset, w, h, confidence=percent)
                )

    return results


def calculate_color_percentage(image, color_ranges, box=None):
    # Check if the ROI is within the image bounds
    if box is not None:
        if (box.x >= 0 and box.y >= 0 and
            box.x + box.width <= image.shape[1] and  # image.shape[1] is the width of the image
            box.y + box.height <= image.shape[
                0]) and box.width > 0 and box.height > 0:  # image.shape[0] is the height of the image

            # Extract the region of interest (ROI) using slicing

            image = image[box.y:box.y + box.height, box.x:box.x + box.width, :3]
        else:
            # Return some error value or raise an exception
            # For example, return 0 or None
            return 0  # or None, or raise an exception
    else:
        image = image[:, :, :3]
    # Create a mask for the pixels within the desired color range
    mask = cv2.inRange(image,
                       (color_ranges['b'][0], color_ranges['g'][0], color_ranges['r'][0]),
                       (color_ranges['b'][1], color_ranges['g'][1], color_ranges['r'][1]))

    # Calculate the percentage of pixels within the color range
    target_pixels = cv2.countNonZero(mask)
    total_pixels = image.size / 3  # Divide by 3 for an RGB image
    percentage = target_pixels / total_pixels
    return percentage


if __name__ == '__main__':
    file = 'C:\\Users\\ok\Downloads\\ok-baijing (2)\\screenshots\\1.png'
    exists = os.path.exists(file)
    image = cv2.imread(file
                       )
    print(is_close_to_pure_color(image))
