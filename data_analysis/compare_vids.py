import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

VID1_DIR = '/Users/emmabethel/Documents/Capstone/march26_baseline' # #'/Users/emmabethel/Documents/Capstone/march26_mic1' #
VID2_DIR = '/Users/emmabethel/Documents/Capstone/march26_mic0'

# Function to load all grayscale images from the folder
def load_images(folder_path, file_pattern):
    images = []
    index = 0
    while True:
        file_path = os.path.join(folder_path, file_pattern.format(index))
        if not os.path.isfile(file_path):
            break
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            break
        images.append(image)
        index += 10
    return images

# find bounding rectangle of arduino nano within image
def find_arduino(image):
    # Calculate the average image
    # image = average_image(images)

    # cv2.imshow(f'Average Image', image)
    # cv2.waitKey(0) 
    # cv2.destroyAllWindows()
    
    _,thresh = cv2.threshold(image,90,255,cv2.THRESH_BINARY)

    # cv2.imshow('thresholded', thresh)
    # cv2.waitKey(0) 
    # cv2.destroyAllWindows()

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bgr_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # cv2.drawContours(bgr_image, contours, -1, (np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255)), 2)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(bgr_image, (x, y), (x+w, y+h), (np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255)), 2)
        if w * h > 25000 and x > 100 and y > 100:
            # print('DONE')
            # cv2.imshow('Image with Contours', bgr_image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            return x, y, w, h
    
    print('here')
    cv2.imshow('Image with Contours', bgr_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return None


def average_image(images):
    # Calculate the sum of all images
    sum_image = np.sum(images, axis=0, dtype=np.float32)
    
    # Calculate the average image by dividing by the number of images
    average_image = (sum_image / len(images)).astype(np.uint8)

    return average_image

def minmax_pixels(images):
    overall_min = float('inf')
    overall_max = float('-inf')
    for img in images:
        overall_max = max(overall_max, np.max(img))
        overall_min = min(overall_min, np.min(img))

    return overall_min, overall_max

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


if __name__ == "__main__":
    images1 = load_images(f'{VID1_DIR}/radiometric', 'frame_{:06d}.tiff')
    images2 = load_images(f'{VID2_DIR}/radiometric', 'frame_{:06d}.tiff')

    # turning raw thermal data into grayscale images on the same scale
    mi, ma = minmax_pixels(images1 + images2)
    images1 = tiff_to_grayscale(images1, mi, ma)
    images2 = tiff_to_grayscale(images2, mi, ma)

    # finding the arduinos in each video (in order to align frames)
    jpg1 = cv2.imread(f'{VID1_DIR}/preview/frame_000284.jpg', cv2.IMREAD_GRAYSCALE)
    jpg2 = cv2.imread(f'{VID2_DIR}/preview/frame_000284.jpg', cv2.IMREAD_GRAYSCALE)
    x1, y1, w1, h1 = find_arduino(jpg1)
    x2, y2, w2, h2 = find_arduino(jpg2)
    print((x1, y1, w1, h1), (x2, y2, w2, h2))

    # calculating total aboslulte distance between the two videos
    overall_diff = np.zeros(images1[0].shape)

    x_shift = x1 - x2
    for i in range(len(images1)):
        # shifting one image over so that the PCB is in the same place for both frames -- rn this is just using a bounding rect around the whole PCB which as discussed w/ hempstead is not ideal, and also i'm only shifting on the x axis because the videos I tested on happened to align on y
        shifted = np.zeros_like(images2[i])
        shifted[:, x_shift:] = images2[i][:, :-x_shift]
        diff = np.absolute(images1[i] - shifted)

        overall_diff = overall_diff + diff
        
    # plotting absolute distance as a heatmap
    plt.imshow(overall_diff, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Value')
    plt.title('Matrix Heatmap')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.show()
