import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math

# Small image sample
# image_array = np.array([[1, 0, 3, 0, 3, 0, 3, 2, 4, 2, 0, 0],
#                [0, 1, 0, 3, 3, 253, 253, 0, 0, 2, 1, 0],
#                [0, 0, 8, 0, 249, 255, 255, 253, 71, 1, 5, 0],
#                [3, 0, 2, 251, 255, 2, 0, 253, 254, 0, 2, 0],
#                [1, 5, 0, 252, 4, 0, 3, 0, 255, 4, 0, 0],
#                [0, 0, 2, 255, 0, 0, 0, 3, 255, 4, 0, 0],
#                [0, 5, 4, 249, 4, 2, 0, 0, 255, 1, 0, 0],
#                [2, 0, 0, 255, 3, 0, 5, 0, 254, 0, 4, 0],
#                [0, 0, 0, 255, 1, 0, 0, 3, 255, 0, 0, 0],
#                [1, 5, 0, 252, 2, 2, 2, 76, 250, 7, 0, 0],
#                [0, 0, 5, 0, 254, 0, 0, 255, 254, 0, 1, 0],
#                [0, 8, 0, 3, 253, 253, 255, 250, 1, 2, 1, 0],
#                [2, 0, 0, 0, 5, 0, 4, 1, 3, 0, 0, 0],
#                [2, 0, 0, 0, 5, 0, 4, 1, 3, 0, 0, 0]])

# height = 14
# width = 12
# pixel_array_size = 1
# plt.imshow(image_array, cmap='gray')
# plt.show()

# def bilinear_interpolation():


def nearest_neighbour(x_dash, y_dash, height, new_height, width, new_width):
    # Formula:
    # sourceX = int(round(targetX / targetWidth * sourceWidth))
    # sourceY =  int(round(targetY / targetHeight * sourceHeight))

    old_x = int(round( float(x_dash) / float(new_width) * float(width) ) )
    old_y = int(round( float(y_dash) / float(new_height) * float(height) ) )

    return old_x, old_y

def transform_image(new_row_array, image_array, mid_y, mid_x, T_inv, height, new_height, width, new_width):
    for y in range(mid_y, -mid_y, -1):
        for x in range(-mid_x, mid_x, 1):

            # old_x, old_y = affine_matrix(x, y, transform_type, T)

            old_x = T_inv[0, 0] * x + T_inv[1, 0] * y + T_inv[2, 0] * 1
            old_y = T_inv[0, 1] * x + T_inv[1, 1] * y + T_inv[2, 1] * 1

            old_x, old_y = nearest_neighbour(old_x, old_y, height, new_height, width, new_width)

            # srcX = min( old_x, width-1)
            # srcY = min( old_y, height-1)

            if old_x >= mid_x:
                old_x = mid_x - 1 
            if old_y >= mid_y:
                old_y = mid_y - 1

            if old_x <= -mid_x:
                old_x = -mid_x + 1
            if old_y <= -mid_y:
                old_y = -mid_y + 1

            # Correct for center offset
            new_x = x + mid_x
            new_y = y - mid_y

            old_x = old_x + mid_x
            old_y = old_y - mid_y

            new_row_array[int(new_y), int(new_x)] = image_array[int(old_y), int(old_x)]
            # print(new_row_array)
            # plt.imshow(new_row_array, cmap='gray')
            # plt.show()

    plt.imshow(new_row_array)
    plt.show()

def main():
    # Part A
    image_path = 'Figures/letter_i.jpg' 
    image_array = cv2.imread(image_path)
    plt.imshow(image_array)
    plt.show()

    height, width, pixel_array_size = image_array.shape

    # keep image size
    new_height = height
    new_width = width

    new_row_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    mid_x = int(width/2)
    mid_y = int(height/2)

    # Types of matrices:
    # 1. Identity 
    # transform_type = "identity"
    # T = [[1, 0, 0],
    #     [0, 1, 0],
    #     [0, 0, 1]]
    
    # # 2. Scaling 
    # transform_type = "scaling"
    # s = 0.5 # making 3 times bigger
    # T = [[s, 0, 0],
    #     [0, s, 0],
    #     [0, 0, 1]]
    
    # 3. Rotation
    transform_type = "rotation"
    theta = 45
    angle_rad = np.radians(theta)
    T = [[np.cos(angle_rad), np.sin(angle_rad), 0],
         [-np.sin(angle_rad), np.cos(angle_rad), 0],
         [0, 0, 1]]

    # 4. Translation
    # transform_type = "translation"
    # tx = 300 # no. pixels along x
    # ty = 0 # no. pixels along y
    # T = [[1, 0, 0],
    #      [0, 1, 0],
    #      [tx, ty, 1]]

    # 5. Shear vertical 
    # transform_type = "shear_vert"
    # sv = 1
    # T = [[1, 0, 0],
    #      [sv, 1, 0],
    #      [0, 0, 1]]
    
    # 6. Shear horiz 
    # transform_type = "shear_vert"
    # sh = 1
    # T = [[1, sh, 0],
    #      [0, 1, 0],
    #      [0, 0, 1]]

    # Sanity check
    # 1 = T_inv[0, 2] * x + T_inv[1, 2] * y + T_inv[2, 2] * 1
    T_inv = inv(T)
    transform_image(new_row_array, image_array, mid_y, mid_x, T_inv, height, new_height, width, new_width)

if __name__ == "__main__":
    main()