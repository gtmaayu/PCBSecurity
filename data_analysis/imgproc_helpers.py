import os
import cv2
import numpy as np


def is_valid(image):
    std = np.std(image)

    return std > 30

def average_image(images, validation=lambda _: True):
    validated_images = []
    for image in images:
        if validation(image):
            validated_images.append(image)

    # Calculate the sum of all images
    sum_image = np.sum(validated_images, axis=0, dtype=np.float32)
    
    # Calculate the average image by dividing by the number of images
    average_image = (sum_image / len(validated_images)).astype(np.uint8)

    return average_image

# Function to load all grayscale images from the folder
def load_images(folder_path, file_pattern, skip_amt=10, read_flag=cv2.IMREAD_UNCHANGED):
    images = []
    index = 0
    while True:
        file_path = os.path.join(folder_path, file_pattern.format(index))
        if not os.path.isfile(file_path):
            break
        image = cv2.imread(file_path, read_flag)
        if image is None:
            break
        images.append(image)
        index += skip_amt
    return images
