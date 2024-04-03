import cv2
import numpy as np
import matplotlib.pyplot as plt
from imgproc_helpers import load_images, average_image, is_valid
from itertools import combinations

VID1_DIR = '/Users/emmabethel/Documents/Capstone/march26_mic1' # #'/Users/emmabethel/Documents/Capstone/march26_mic1' #
VID2_DIR = '/Users/emmabethel/Documents/Capstone/march26_mic0'


def find_intersection(l1, l2):
    x1, y1 = l1[0], l1[1]
    x2, y2 = l1[2], l1[3]
    x3, y3 = l2[0], l2[1]
    x4, y4 = l2[2], l2[3]

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None  # Lines are parallel or coincident, no intersection

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den

    return round(px), round(py)

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

def calculate_y_intercept(point, slope):
    x, y = point
    return y - slope * x

def calculate_y_intercept_difference(line1, line2):
    x1, y1 = line1[0], line1[1]
    x2, y2 = line1[2], line1[3]
    slope1 = (y2 - y1) / (x2 - x1)

    x1, y1 = line2[0], line2[1]
    x2, y2 = line2[2], line2[3]
    slope2 = (y2 - y1) / (x2 - x1)

    b1 = calculate_y_intercept((line1[0], line1[1]), slope1)
    b2 = calculate_y_intercept((line2[0], line2[1]), slope2)

    return abs(b1 - b2)

def full_shift(img, pos_diffs):
    new_img = img

    if pos_diffs[0] != 0:
        new_img = shift_by(new_img, pos_diffs[0], False)
    if pos_diffs[1] != 0:
        new_img = shift_by(new_img, pos_diffs[1], True)
    
    return new_img

def find_center_chip(img):
    color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # _,thresh = cv2.threshold(img,135,255,cv2.THRESH_TOZERO)
    # cv2.imshow("thresholded", thresh)
   
    edges = cv2.Canny(img, 100, 200)
    # contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Detect lines using Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=25, minLineLength=15, maxLineGap=5)

    # cv2.imshow("hello", edges)

    # Initialize list to store slopes and lines
    slopes = []
    filtered_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 != 0:  # Avoid division by zero
            slope = (y2 - y1) / (x2 - x1)
            slopes.append(slope)
            filtered_lines.append(line[0])

    # Sort lines based on slope magnitude
    absolute_diff = [abs(1 - s) for s in slopes]
    absolute_diff_neg_1 = [abs(-1 - s) for s in slopes]
    sorted_indices = np.argsort(absolute_diff)
    d = 0
    i = 0
    while d < 10:
        closest_to_1_indices = sorted_indices[i:i + 2]  # Select the 4 lines with absolute slope values closest to 1
        d = calculate_y_intercept_difference(filtered_lines[closest_to_1_indices[0]], filtered_lines[closest_to_1_indices[1]])
        i += 1

    sorted_indices_neg_1 = np.argsort(absolute_diff_neg_1)
    d = 0
    i = 0
    while d < 10:
        closest_to_neg_1_indices = sorted_indices_neg_1[i:i + 2]  # Select the 4 lines with absolute slope values closest to 1
        d = calculate_y_intercept_difference(filtered_lines[closest_to_neg_1_indices[0]], filtered_lines[closest_to_neg_1_indices[1]])
        i += 1

    final_lines = np.concatenate((closest_to_neg_1_indices, closest_to_1_indices))


    # Draw selected lines on the original image
    for i in range(len(filtered_lines)):
        if i in final_lines:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        line = filtered_lines[i]
        x1, y1, x2, y2 = line
        cv2.line(color_img, (x1, y1), (x2, y2), color, 1)

    corners = []
    for i, j in list(combinations(final_lines, 2)):
        if slopes[i] * slopes[j] < 0:  # different signs
            corners.append(find_intersection(filtered_lines[i], filtered_lines[j]))

            cv2.circle(color_img, corners[-1], 2, (255, 0, 0), -1)

    # cv2.drawContours(color_img, new_contours, -1, (0, 255, 0), 1)
    # cv2.imshow('aaaa', color_img)
    # okay maybe find the 4 edge lines of the big chip? and then their intersection points are your keypoints?

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    corners.sort(key=lambda x: x[0])
    if corners[1][1] > corners[2][1]:
        temp = corners[1]
        corners[1] = corners[2]
        corners[2] = temp

    return corners


def get_shift_amount(src, dest):
    corners1 = find_center_chip(src)
    corners2 = find_center_chip(dest)

    rightmost1 = np.array(corners1[3])
    rightmost2 = np.array(corners2[3])

    return rightmost2 - rightmost1


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


def filter_jpgs(l1, l2, is_valid):
    l1_ret = []
    l2_ret = []

    for i in range(len(l1)):
        if is_valid(l1[i]) and is_valid(l2[i]):
            l1_ret.append(l1[i])
            l2_ret.append(l2[i])

    return l1_ret, l2_ret


if __name__ == "__main__":
    images1 = load_images(f'{VID1_DIR}/radiometric', 'frame_{:06d}.tiff')
    images2 = load_images(f'{VID2_DIR}/radiometric', 'frame_{:06d}.tiff')

    # figuring out how much to shift video 1 over by to put the arduino in the same spot as in video 2
    jpg1 = load_images(f'{VID1_DIR}/preview', 'frame_{:06d}.jpg', read_flag=cv2.IMREAD_GRAYSCALE)
    jpg2 = load_images(f'{VID2_DIR}/preview', 'frame_{:06d}.jpg', read_flag=cv2.IMREAD_GRAYSCALE)

    avg1 = average_image(jpg1, is_valid)
    avg2 = average_image(jpg2, is_valid)

    shift_amount = get_shift_amount(avg1, avg2)

    # calculating total aboslulte distance between the two videos
    overall_diff = np.zeros(images1[0].shape)

    for i in range(len(images1)):
        # shifting one image over so that the PCB is in the same place for both frames
        shifted = full_shift(images1[i], shift_amount)
        # shifted = images1[i]

        diff = np.absolute((images2[i].astype(np.int16) - shifted.astype(np.int16)))

        overall_diff = overall_diff + diff

    overall_diff = 0.04 * overall_diff / len(images1)  # multiplying by 0.04 supposedly translates raw radiometric data to kelvin

    overall_diff = full_shift(overall_diff, - 1 * shift_amount)
        
    # plotting absolute distance as a heatmap
    plt.imshow(overall_diff, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Average Difference (Kelvin/Celsius)')
    plt.clim(0, 3.5)
    plt.title('Microphone vs Microphone (same board)')
    plt.show()
