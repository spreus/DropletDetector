import os
from datetime import datetime

import cv2

from Dtos.DropletDto import DropletDto
from Dtos.RoiDto import RoiDto
from Functions.files import extract_info_from_filename


def process_images_in_directory(directory_path: str, roi: RoiDto, output_directory: str) -> list:
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            volume, timestamp = extract_info_from_filename(filename)

            image_path = os.path.join(directory_path, filename)

            print(f"Processing {image_path}")
            droplets, output_path = detect_droplets(image_path, roi, output_directory)
            if len(droplets) == 1:
                for i, droplet in enumerate(droplets):
                    droplet_dto = DropletDto(
                        image_filepath=os.path.basename(output_path),
                        volume=volume,
                        timestamp=timestamp,
                        seconds=0,
                        center=droplet['center'],
                        radius=droplet['radius'],
                        area=droplet['area']
                    )
                    data.append(droplet_dto)

    # Sort
    sorted_droplets = sorted(data, key=lambda x: x.timestamp)
    t0 = sorted_droplets[0].timestamp
    for droplet in sorted_droplets:
        droplet.seconds = difference_in_seconds(t0, droplet.timestamp)

    return sorted_droplets


def detect_droplets(image_path: str, roi: RoiDto, output_dir: str):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Crop the image to the ROI
    # cropped_image = image[roi.y:roi.y + roi.h, roi.x:roi.x + roi.w]

    # Convert to grayscale and threshold
    # gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to the image
    _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    droplets = []

    for contour in contours:
        if is_valid_droplet(contour, roi):
            # Get the minimum enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Calculate the area
            area = cv2.contourArea(contour)

            # Store the droplet properties
            droplets.append({
                'center': center,
                'radius': radius,
                'area': area
            })

            # Draw the circle around the droplet
            cv2.circle(image, center, radius, (0, 255, 0), 2)  # Green color, thickness of 2

            # Optionally, draw the center of the droplet
            cv2.circle(image, center, 2, (0, 0, 255), -1)  # Red color, filled circle

    # Save the result image
    image_name_res = os.path.basename(image_path)
    output_path = output_dir + "/" + image_name_res + " - result.jpg"
    cv2.imwrite(output_path, image)
    print(f"Image saved to {output_path}")

    return droplets, output_path


def is_valid_droplet(contour: cv2.typing.MatLike, roi: RoiDto) -> bool:
    (x, y), radius = cv2.minEnclosingCircle(contour)

    return int(radius) > 3 and roi.x < x < (roi.x + roi.w) and roi.y < y < (roi.y + roi.h)


def select_roi(image_path: str) -> RoiDto:
    # Load the image
    image = cv2.imread(image_path)

    # Let the user select the ROI
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)

    # Close the ROI selection window
    cv2.destroyWindow("Select ROI")

    # roi is a tuple of (x, y, w, h)
    return RoiDto(
        x=roi[0],
        y=roi[1],
        w=roi[2],
        h=roi[3]
    )


def difference_in_seconds(timestamp1, timestamp2):
    # Define the format of the timestamp
    fmt = '%Y-%m-%d %H:%M:%S%f'

    # Convert the string timestamps to datetime objects
    time1 = datetime.strptime(timestamp1, fmt)
    time2 = datetime.strptime(timestamp2, fmt)

    # Calculate the difference in seconds
    difference = abs((time1 - time2).total_seconds())

    return difference
