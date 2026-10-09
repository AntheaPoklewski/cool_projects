import numpy as np
from numpy.linalg import inv
import cv2
import matplotlib.pyplot as plt

def bilinear_interpolation(x_dash, y_dash, image_array, height, new_height, width, new_width, mid_x, mid_y):
    old_x = float(x_dash) / float(new_width) * float(width)
    old_y = float(y_dash) / float(new_height) * float(height)

    # Get integer coordinates of the four surrounding pixels
    x1 = int(np.floor(old_x))
    y1 = int(np.floor(old_y))
    x2 = x1 + 1
    y2 = y1 + 1

    # Clamp coordinates to image bounds
    # if x1 > mid_x:
    #     x1 = max(0, min(x1, mid_x))
    # if x2 > mid_x:
    #     x2 = max(0, min(x2, mid_x))
    # if y1 > mid_y:
    #     y1 = max(0, min(y1, mid_y))
    # if y2 > mid_y:
    #     y2 = max(0, min(y2, mid_y))

    # if x1 < -mid_x:
    #     x1 = max(0, min(x1, -mid_x))
    # if x2 < -mid_x:
    #     x2 = max(0, min(x2, -mid_x))
    # if y1 < -mid_y:
    #     y1 = max(0, min(y1, -mid_y))
    # if y2 < -mid_y:
    #     y2 = max(0, min(y2, -mid_y))

    if x1 >= mid_x:
        x1 = mid_x - 1
    if y1 >= mid_y:
        y1 = mid_y - 1
    if x1 <= -mid_x:
        x1 = -mid_x + 1
    if y1 <= -mid_y:
        y1 = -mid_y + 1

    if x2 >= mid_x:
        x2 = mid_x - 1
    if y2 >= mid_y:
        y2 = mid_y - 1
    if x2 <= -mid_x:
        x2 = -mid_x + 1
    if y2 <= -mid_y:
        y2 = -mid_y + 1

    # Get fractional parts for interpolation weights
    dx = abs(old_x) - abs(x1)
    dy = abs(old_y) - abs(y1)

    # Adjust for center offset to get image array indices
    # Boundary checking in centered coordinate system (matching original logic)
    if old_x >= mid_x:
        old_x = mid_x - 1
    if old_y >= mid_y:
        old_y = mid_y - 1
    if old_x <= -mid_x:
        old_x = -mid_x + 1
    if old_y <= -mid_y:
        old_y = -mid_y + 1

    old_x = old_x + mid_x
    old_y = old_y - mid_y
    x1 = x1 + mid_x
    x2 = x2 + mid_x
    y1 = y1 - mid_y
    y2 = y2 - mid_y

    # Get the four pixel value
    if len(image_array.shape) == 3:  # Color image
        p11 = image_array[y1, x1].astype(np.float32)
        p21 = image_array[y1, x2].astype(np.float32)
        p12 = image_array[y2, x1].astype(np.float32)
        p22 = image_array[y2, x2].astype(np.float32)
    else:  # Grayscale image
        p11 = float(image_array[y1, x1])
        p21 = float(image_array[y1, x2])
        p12 = float(image_array[y2, x1])
        p22 = float(image_array[y2, x2])

    # Bilinear interpolation
    # Interpolate along x-axis first
    p1 = p11 * (1 - dx) + p21 * dx
    p2 = p12 * (1 - dx) + p22 * dx
    
    # Interpolate along y-axis
    interpolated = p1 * (1 - dy) + p2 * dy
    
    # Convert back to uint8
    if len(image_array.shape) == 3:
        return np.clip(interpolated, 0, 255).astype(np.uint8)
    else:
        return np.clip(int(interpolated), 0, 255)

def nearest_neighbour(x_dash, y_dash, height, new_height, width, new_width, mid_x, mid_y):
    # Formula:
    # sourceX = int(round(targetX / targetWidth * sourceWidth))
    # sourceY =  int(round(targetY / targetHeight * sourceHeight))

    old_x = int(round(float(x_dash)/float(new_width) * float(width)))
    old_y = int(round(float(y_dash)/float(new_height) * float(height)))

    if old_x >= mid_x:
        old_x = mid_x - 1 
    if old_y >= mid_y:
        old_y = mid_y - 1

    if old_x <= -mid_x:
        old_x = -mid_x + 1
    if old_y <= -mid_y:
        old_y = -mid_y + 1

    old_x = old_x + mid_x
    old_y = old_y - mid_y

    return old_x, old_y

def transform_image(new_row_array, image_array, mid_y, mid_x, T_inv, height, new_height, width, new_width, type_int):
    for y in range(mid_y, -mid_y, -1):
        for x in range(-mid_x, mid_x, 1):

            # old_x, old_y = affine_matrix(x, y, transform_type, T)
            old_x = T_inv[0, 0] * x + T_inv[1, 0] * y + T_inv[2, 0] * 1
            old_y = T_inv[0, 1] * x + T_inv[1, 1] * y + T_inv[2, 1] * 1

            # Correct for center offset
            new_x = x + mid_x
            new_y = y - mid_y

            if type_int == "NN":
                old_x, old_y = nearest_neighbour(old_x, old_y, height, new_height, width, new_width, mid_x, mid_y)
                new_row_array[int(new_y), int(new_x)] = image_array[int(old_y), int(old_x)]
            if type_int == "BI":
                interpolated_pixel = bilinear_interpolation(old_x, old_y, image_array, height, new_height, width, new_width, mid_x, mid_y)
                new_row_array[int(new_y), int(new_x)] = interpolated_pixel

            # srcX = min( old_x, width-1)
            # srcY = min( old_y, height-1)

            # print(new_row_array)
            # plt.imshow(new_row_array, cmap='gray')
            # plt.show()
    return new_row_array

def select_transform(save_path, image_array, transform_type, integration_type, height, width, pixel_array_size):
    # Keep image size
    new_height = height
    new_width = width

    # New image frame
    new_row_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    mid_x = int(width/2)
    mid_y = int(height/2)

    # Types of matrices:
    match transform_type:
        # 1. Identity 
        case "identity":
            T = [[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]]
    
        # 2. Scaling 
        case "scaling":
            s = 30 # making 3 times bigger
            T = [[s, 0, 0],
                [0, s, 0],
                [0, 0, 1]]
    
        # 3. Rotation
        case "rotation":
            theta = 45
            angle_rad = np.radians(theta)
            T = [[np.cos(angle_rad), np.sin(angle_rad), 0],
                [-np.sin(angle_rad), np.cos(angle_rad), 0],
                [0, 0, 1]]

        # 4. Translation
        case "translation":
            tx = 300 # no. pixels along x
            ty = 0 # no. pixels along y
            T = [[1, 0, 0],
                [0, 1, 0],
                [tx, ty, 1]]

        # 5. Shear vertical 
        case "shear_vert":
            sv = 1
            T = [[1, 0, 0],
                 [sv, 1, 0],
                 [0, 0, 1]]
    
        # 6. Shear horiz 
        case "shear_horiz":
            sh = 1
            T = [[1, sh, 0],
                 [0, 1, 0],
                 [0, 0, 1]]
            
            
    match integration_type:
        case "nearest_neighbour":
            type_int = "NN"
        case "bilinear":
            type_int = "BI"

    # Sanity check
    # 1 = T_inv[0, 2] * x + T_inv[1, 2] * y + T_inv[2, 2] * 1

    T_inv = inv(T)
    # Choose type of interpolation method -> NN = Nearest Neighbour
    trans_image = transform_image(new_row_array, image_array, mid_y, mid_x, T_inv, height, new_height, width, new_width, type_int)
    plt.imshow(trans_image)
    plt.show()

    # Create figure and axis
    fig, ax = plt.subplots()

    # Show image
    ax.imshow(trans_image)

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    fig.savefig(f"{save_path}affine_{transform_type}_{integration_type}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    
    # Small image sample
    # image_array = np.array([[1, 0, 3, 0, 3, 0, 3, 2, 4, 2, 0, 0],
    #             [0, 1, 0, 3, 3, 253, 253, 0, 0, 2, 1, 0],
    #             [0, 0, 8, 0, 249, 255, 255, 253, 71, 1, 5, 0],
    #             [3, 0, 2, 251, 255, 2, 0, 253, 254, 0, 2, 0],
    #             [1, 5, 0, 252, 4, 0, 3, 0, 255, 4, 0, 0],
    #             [0, 0, 2, 255, 0, 0, 0, 3, 255, 4, 0, 0],
    #             [0, 5, 4, 249, 4, 2, 0, 0, 255, 1, 0, 0],
    #             [2, 0, 0, 255, 3, 0, 5, 0, 254, 0, 4, 0],
    #             [0, 0, 0, 255, 1, 0, 0, 3, 255, 0, 0, 0],
    #             [1, 5, 0, 252, 2, 2, 2, 76, 250, 7, 0, 0],
    #             [0, 0, 5, 0, 254, 0, 0, 255, 254, 0, 1, 0],
    #             [0, 8, 0, 3, 253, 253, 255, 250, 1, 2, 1, 0],
    #             [2, 0, 0, 0, 5, 0, 4, 1, 3, 0, 0, 0],
    #             [2, 0, 0, 0, 5, 0, 4, 1, 3, 0, 0, 0]])

    # height = 14
    # width = 12
    # pixel_array_size = 1
    # plt.imshow(image_array, cmap='gray')
    # plt.show()

    image_path = 'Assignment_1/Figures/letter_i.jpg' 
    image_array = cv2.imread(image_path)
    height, width, pixel_array_size = image_array.shape

    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    # Show image
    plt.imshow(image_array)
    plt.show()

    # # Create figure and axis
    # fig, ax = plt.subplots()

    # # Show image
    # ax.imshow(image_array)

    # # Add labels
    # ax.set_xlabel("X Pixel Coordinate")
    # ax.set_ylabel("Y Pixel Coordinate")

    # # # Save
    # # fig.savefig(f"{save_path}affine_original.pdf", bbox_inches="tight")
    # # plt.close(fig)

    # transform_type = "scaling" # "shear_horiz" #"translation" # "rotation" #"identity" # "shear_vert"
    # integration_type = "bilinear" #  # "nearest_neighbour" #

    # select_transform(save_path, image_array, transform_type, integration_type, height, width, pixel_array_size)
    # # Save

    # Bilinear library
    # Enlarge image by 2x
    resized = cv2.resize(image_array, None, fx=30, fy=30, interpolation=cv2.INTER_LINEAR)
    plt.imshow(resized)
    plt.show()

    # Create figure and axis
    fig, ax = plt.subplots()

    # Show image
    ax.imshow(resized)

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    scale = 30
    h_new = height * scale
    w_new = width * scale

    # Crop region corresponding to original 1×1 pixel area
    start_h = int(h_new/2) 
    start_w = int(w_new/2)

    cropped = resized[start_h - int(height/2):start_h + int(height/2), start_w - int(width/2):start_w + int(width/2)]

    plt.imshow(cropped)
    plt.show()

    # Create figure and axis
    fig, ax = plt.subplots()

    # Show image
    ax.imshow(cropped)

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # # Save
    # fig.savefig(f"{save_path}affine_{transform_type}_{integration_type}.pdf", bbox_inches="tight")
    # plt.close(fig)

if __name__ == "__main__":
    main()