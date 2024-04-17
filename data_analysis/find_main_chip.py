import cv2
import numpy as np
from itertools import combinations

IMG_PATH = '/Users/emmabethel/Documents/Classes/Capstone/PCBSecurity/RecordedVideos_april15_microphoneBoardB_0_raw_screenshot.png'


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


def find_center_chip(img):
    color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # _,thresh = cv2.threshold(img,135,255,cv2.THRESH_TOZERO)
    # cv2.imshow("thresholded", thresh)
   
    edges = cv2.Canny(img, 100, 200)
    # contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=25, minLineLength=15, maxLineGap=5)

    # cv2.imshow("hello", edges)
    # cv2.waitKey(0)

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
    while d < 30:
        closest_to_1_indices = sorted_indices[i:i + 2]  # Select the 2 lines with absolute slope values closest to 1
        d = calculate_y_intercept_difference(filtered_lines[closest_to_1_indices[0]], filtered_lines[closest_to_1_indices[1]])
        i += 1

    sorted_indices_neg_1 = np.argsort(absolute_diff_neg_1)
    d = 0
    i = 0
    while d < 30:
        closest_to_neg_1_indices = sorted_indices_neg_1[i:i + 2]  # Select the 2 lines with absolute slope values closest to 1
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

    # cv2.imshow("hello", color_img)
    # cv2.waitKey(0)

    corners.sort(key=lambda x: x[0])
    if corners[1][1] > corners[2][1]:
        temp = corners[1]
        corners[1] = corners[2]
        corners[2] = temp

    return corners

def find_atmega_right_corner(img):
    corners = find_center_chip(img)

    for x,y in corners:
        if 535 <= x <= 560 and 350 <= y <= 400:
            return (x,y) 

if __name__ == "__main__":
    # figuring out how much to shift video 1 over by to put the arduino in the same spot as in video 2
    img = cv2.imread(IMG_PATH, cv2.IMREAD_GRAYSCALE)


    corner = find_atmega_right_corner(img)

    print(corner)
