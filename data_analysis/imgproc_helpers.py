import os
import cv2
import numpy as np


def shift_by(img, shift_amount, vertical=False):
    new_img = np.zeros_like(img)
    if vertical:
        if shift_amount > 0:
            new_img[shift_amount:, :] = img[:-shift_amount, :]
        else:
            new_img[:shift_amount, :] = img[-shift_amount:, :]
    else:
        if shift_amount > 0:
            new_img[:, shift_amount:] = img[:, :-shift_amount]
        else:
            new_img[:, :shift_amount] = img[:, -shift_amount:]
    
    return new_img

def shift_img(img, pos_diffs):
    new_img = img

    if pos_diffs[0] != 0:
        new_img = shift_by(new_img, pos_diffs[0], False)
    if pos_diffs[1] != 0:
        new_img = shift_by(new_img, pos_diffs[1], True)
    
    return new_img

def read_alignment_vals(vid_dir):
    # Open the file in read mode ('r')
    with open(f'{vid_dir}/alignment.txt', 'r') as file:
        # Read one line from the file
        line = file.readline()
        # Check if line is not empty
        if line:
            # Split the line into two numbers
            numbers = line.split(',')
            # Extract the numbers
            return np.array([int(numbers[0].strip()), int(numbers[1].strip())])
        
    return None


def is_valid(image, thresh=29):
    std = np.std(image)

    print(std)

    return std > thresh

def tiff_to_grayscale(images, mi, ma):
    pixrange = ma - mi
    res = []
    for img in images:
        new_img = img - mi
        new_img = 255 * new_img / pixrange
        new_img = np.round(new_img)
        new_img = new_img.astype(np.uint8)

        res.append(new_img)

    return res

def minmax_pixels(images):
    overall_min = float('inf')
    overall_max = float('-inf')
    for img in images:
        overall_max = max(overall_max, np.max(img))
        overall_min = min(overall_min, np.min(img))

    return overall_min, overall_max

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
