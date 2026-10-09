import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math

def filter_image(image_path, filter_type, m):
    image_array = cv2.imread(image_path)
    height, width, pixel_array_size = image_array.shape
    
    # Create figure and axis
    fig, ax = plt.subplots()

    ax.imshow(image_array, cmap='gray')

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}spatial_filt_{filter_type}_orig.pdf", bbox_inches="tight")
    plt.close(fig)

    # Plot image
    plt.imshow(image_array, cmap='gray')
    plt.show()

    # Keep image size
    new_height = height
    new_width = width

    # New image frame
    new_row_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    mid_x = int(width/2)
    mid_y = int(height/2)

    match filter_type:
        case "average":
            new_array = uniform_neighbourhood_averaging(image_array, m)

        case "gaussian":
            # Apply Gaussian filter
            kernel_size = 5
            sigma = 3
            blurred = gaussian_filter_rgb(image_array, kernel_size, sigma)
            # Clip values to valid range
            new_array = np.clip(blurred, 0, 255)

        case "range":
            range_type = "median" # "max" # "min" #
            new_array = calc_median_min_max(image_array, m, range_type)

        case "laplace":
            type_laplace = "basic" # "diagonal" # "literature" #
            new_array = laplace(image_array, type_laplace)    

        case "sobel":
            new_array = x_y_sobel(image_array)

    plt.imshow(new_array, cmap='gray')
    plt.show()

    # Create figure and axis
    fig, ax = plt.subplots()

    ax.imshow(new_array, cmap='gray')

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}spatial_filt_{filter_type}.pdf", bbox_inches="tight")
    plt.close(fig)

def uniform_neighbourhood_averaging(image_array, m):
    height, width, pixel_array_size = image_array.shape
    average_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    
    for y in range(0, height, 1):
        for x in range(0, width, 1):
            num_pixels = 0
            p_array = []

            for y_m in range(0, m, 1):
                for x_m in range(0, m, 1):
                    check = clamp_vals((x + x_m), (y + y_m), width, height)
                    if check == True:
                        p_array.append(image_array[(y + y_m), (x + x_m)])
                        num_pixels += 1

            s = calc_average(p_array, num_pixels) 
            average_array[y, x] = s

            if average_array[y, x].ndim == 0:  # grayscale pixel
                average_array[y, x] = np.uint8(np.clip(s, 0, 255))
            else:  # color pixel (length-3 array)
                average_array[y, x] = np.clip(average_array[y, x], 0, 255).astype(np.uint8)
    
    return average_array

def gaussian_kernel(size, sigma):
    """Create a 2D Gaussian kernel"""
    # Create coordinate grids
    ax = np.arange(-size // 2 + 1, size // 2 + 1)
    xx, yy = np.meshgrid(ax, ax)
    # Gaussian formula
    kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
    kernel_norm = kernel / np.sum(kernel)
    # print(xx)
    # print(yy)
    # print(kernel_norm)

    # Normalize so sum = 1
    return kernel / np.sum(kernel)

def convolve2d(image, kernel, convolve_type):
    """Manual 2D convolution"""
    # Get dimensions
    img_height, img_width = image.shape
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2
    
    # Pad the image to handle borders
    padded = np.pad(image, pad, mode='edge')

    # Output array
    if convolve_type == "gaussian":
        output = np.zeros_like(image)
    elif convolve_type == "laplace" or convolve_type == "sobel":
        output = np.zeros_like(image, dtype=np.float64)
    
    # Perform convolution
    for i in range(img_height):
        for j in range(img_width):
            # Extract region
            region = padded[i:i+kernel_size, j:j+kernel_size]
            # Apply kernel (element-wise multiply and sum)
            output[i, j] = np.sum(region * kernel)
    
    return output

def gaussian_filter_rgb(image, kernel_size, sigma):
    """Apply Gaussian filter to RGB image"""
    # Create the Gaussian kernel
    kernel = gaussian_kernel(kernel_size, sigma)
    
    # Apply to each color channel separately
    filtered = np.zeros_like(image, dtype=np.float64)
    
    channel = 0  # R, G, B
    filtered = convolve2d(image[:, :, channel], kernel, convolve_type="gaussian")
    
    return filtered

def clamp_vals(x_test, y_test, width, height):
    val_x = val_y = True

    if x_test >= width:
        val_x = False
    if x_test < 0:
        val_x = False
    if y_test >= height:
        val_y = False
    if y_test < 0:
        val_y = False

    if (val_x == False) or (val_y == False):
        return False
    else:
        return True

def calc_average(array_region, num_pixels):
    if isinstance(array_region, np.ndarray):
        # If it's a numpy array (3D image), extract R channel
        gray_values = array_region[:, :, 0]   # take R channel
        # Flatten to 1D for histogram
        gray_values = gray_values.flatten()
    else:
        # If it's a list of pixels, extract R channel (first element) from each pixel
        gray_values = [int(pixel[0]) for pixel in array_region]

    R = 1/num_pixels
    sum = 0

    for val in gray_values:
        sum = sum + val
    
    average_value = np.uint8(R * sum)
    return average_value

def order_pixels(p_array):
    if isinstance(p_array, np.ndarray):
        # If it's a numpy array (3D image), extract R channel
        gray_values = p_array[:, :, 0]   # take R channel
        # Flatten to 1D for histogram
        gray_values = gray_values.flatten()
    else:
        # If it's a list of pixels, extract R channel (first element) from each pixel
        gray_values = [int(pixel[0]) for pixel in p_array]
    
    sorted_array = sorted(gray_values)
    return sorted_array

def calc_median_min_max(image_array, m, range_type):
    height, width, pixel_array_size = image_array.shape
    average_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    
    for y in range(0, height, 1):
        for x in range(0, width, 1):
            num_pixels = 0
            p_array = []

            for y_m in range(0, m, 1):
                for x_m in range(0, m, 1):
                    check = clamp_vals((x + x_m), (y + y_m), width, height)
                    if check == True:
                        p_array.append(image_array[(y + y_m), (x + x_m)])
                        num_pixels += 1     
            
            ordered = order_pixels(p_array)
            if range_type == "min":
                s = ordered[0]
            elif range_type == "max":
                s = ordered[-1]
            elif range_type == "median":
                s = ordered[round(len(p_array)/2)]

            average_array[y, x] = s

            if average_array[y, x].ndim == 0:  # grayscale pixel
                average_array[y, x] = np.uint8(np.clip(s, 0, 255))
            else:  # color pixel (length-3 array)
                average_array[y, x] = np.clip(average_array[y, x], 0, 255).astype(np.uint8)
    
    return average_array

def laplace(image_array, type_laplace):
    match type_laplace:
        case "basic":
            kernel = np.array([ [0, 1, 0],
                                [1, -4, 1],
                                [0, 1, 0]], dtype=np.float64)
            
        case "diagonal":
            kernel = np.array([ [0, 1, 0],
                                [1, -4, 1],
                                [0, 1, 0]], dtype=np.float64)
            
        case "literature":
            kernel = np.array([ [0, -1, 0],
                                [-1, 4, -1],
                                [0, -1, 0]], dtype=np.float64)
            
    # Apply to each color channel separately
    filtered = np.zeros_like(image_array, dtype=np.float64)
    
    channel = 0  # R, G, B
    filtered = convolve2d(image_array[:, :, channel], kernel, convolve_type="laplace")

    # plt.imshow(filtered, cmap='gray')
    # plt.show()

    # # Create figure and axis
    # fig, ax = plt.subplots()

    # ax.imshow(filtered, cmap='gray')

    # # Add labels
    # ax.set_xlabel("X Pixel Coordinate")
    # ax.set_ylabel("Y Pixel Coordinate")

    # # Save
    # save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    # fig.savefig(f"{save_path}spatial_filt_laplace_mask.pdf", bbox_inches="tight")
    # plt.close(fig)

    match type_laplace:
        case "basic":
            filtered = image_array[:, :, channel] - filtered

        case "diagonal":
            filtered = image_array[:, :, channel] + filtered

        case "literature":
            filtered = image_array[:, :, channel] - filtered

    return filtered
    
def x_y_sobel(image_array):
    # Apply to each color channel separately
    filtered = np.zeros_like(image_array, dtype=np.float64)
    channel = 0  # R, G, B

    kernel = np.array([ [-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    filtered_x = convolve2d(image_array[:, :, channel], kernel, convolve_type="sobel")
    

    kernel = np.array([ [-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]], dtype=np.float64)
    filtered_y = convolve2d(image_array[:, :, channel], kernel, convolve_type="sobel")

    filtered = np.sqrt(filtered_x ** 2 + filtered_y ** 2)
    return filtered

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
    # test(image_array, height, width, pixel_array_size)

    filter_type = "sobel" # "laplace" # "range" # "gaussian" # "average" # None # 

    match filter_type:
        case "average":
            m = 9
            image_path = 'Figures/spatial_filtering.png' 
            filter_image(image_path, filter_type, m)

        case "gaussian":
            m = 3
            image_path = 'Figures/gaussian.png' 
            filter_image(image_path, filter_type, m)

        case "range":
            m = 3
            image_path = 'Figures/min_max_median.png' 
            filter_image(image_path, filter_type, m)

        case "laplace":
            m = None
            image_path = 'Figures/laplace.png' 
            filter_image(image_path, filter_type, m)
            # image_array = cv2.imread(image_path)
            # laplacian = cv2.Laplacian(image_array[:, :, 0], cv2.CV_64F)
            # cv2.imwrite("laplacian.png", laplacian)

        case "sobel":
            m = None
            image_path = 'Figures/sobel.png' 
            filter_image(image_path, filter_type, m)

if __name__ == "__main__":
    main()