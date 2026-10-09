import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math
           
def log_transformation(image_array, x, y):
    pixel = image_array[y, x].astype(np.float32) 
    """
    Log transform for a single pixel. Works for both grayscale and color.
    Uses NumPy so it can handle a 3-element RGB array (math.log expects a scalar).
    """
    max_val = np.max(image_array)
    c = 255.0 / (np.log1p(max_val) / np.log(2.0))  
    
    # log base 2: log2(1 + pixel) = ln(1+pixel) / ln(2)
    s = c * (np.log1p(pixel) / np.log(2.0))

    if pixel.ndim == 0:  # grayscale pixel
        return np.uint8(np.clip(s, 0, 255))
    else:  # color pixel (length-3 array)
        return np.clip(s, 0, 255).astype(np.uint8)

def gamma_transformation(image_array, x, y):
    pixel = image_array[y, x].astype(np.float32) 
    gamma_val = 1/(2.5)
    c = 1
    s = c * 255 * (pixel / 255) ** gamma_val

    if pixel.ndim == 0:  # grayscale pixel
        return np.uint8(np.clip(s, 0, 255))
    else:  # color pixel (length-3 array)
        return np.clip(s, 0, 255).astype(np.uint8)

def contrast_stretch_transformation(image_array, x, y):
    pixel = image_array[y, x].astype(np.float32) 
    # Calc min and max values 
    min_val = np.min(image_array)
    max_val = np.max(image_array)
    c = 255.0 # -> maximum is white 
    
    # Apply contrast stretching 
    s = (pixel - min_val) * (c / (max_val - min_val))

    if pixel.ndim == 0:  # grayscale pixel
        return np.uint8(np.clip(s, 0, 255))
    else:  # color pixel (length-3 array)
        return np.clip(s, 0, 255).astype(np.uint8)

def intensity_level_slicing(image_array, x, y):
    pixel = image_array[y, x].astype(np.float32) # value in range 0 - 255 (black - white)
    # # Calc min and max values 
    # min_val = np.min(image_array)
    # max_val = np.max(image_array)
    
    # Create range -> preserve range
    A = 150
    B = 255
    C = 0

    s = []
    # for element in pixel:
    #     if (element >= A) and (element <= B):
    #         s.append(B)
    #     else:
    #         s.append(element)

    # Create range -> reduce range
    for element in pixel:
        if (element >= A) and (element <= B):
            s.append(B)
        else:
            s.append(C)


    if pixel.ndim == 0:  # grayscale pixel
        return np.uint8(np.clip(s, 0, 255))
    else:  # color pixel (length-3 array)
        return np.clip(s, 0, 255).astype(np.uint8)

def light_dark_transformation(image_array, x, y):
    pixel = image_array[y, x].astype(np.float32) 
    # Apply light and dark -> dark < 1.0 < light
    c = 0.8 # -> dark
    # c = 1.8 # -> light
    s = pixel * c

    if pixel.ndim == 0:  # grayscale pixel
        return np.uint8(np.clip(s, 0, 255))
    else:  # color pixel (length-3 array)
        return np.clip(s, 0, 255).astype(np.uint8)

def transform_image(image_path, transform_type):
    image_array = cv2.imread(image_path)
    height, width, pixel_array_size = image_array.shape
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

    match transform_type:
        case "log":
            for y in range(0, height, 1):
                for x in range(0, width, 1):
                    pixel = log_transformation(image_array, x, y)
                    new_row_array[y, x] = pixel

        case "gamma":
            for y in range(0, height, 1):
                for x in range(0, width, 1):
                    pixel = gamma_transformation(image_array, x, y)
                    new_row_array[y, x] = pixel

        case "contrast":
            for y in range(0, height, 1):
                for x in range(0, width, 1):
                    pixel = contrast_stretch_transformation(image_array, x, y)
                    new_row_array[y, x] = pixel

        case "intense_slicing":
            for y in range(0, height, 1):
                for x in range(0, width, 1):
                    pixel = intensity_level_slicing(image_array, x, y)
                    new_row_array[y, x] = pixel

        case "light_dark":
            for y in range(0, height, 1):
                for x in range(0, width, 1):
                    pixel = light_dark_transformation(image_array, x, y)
                    new_row_array[y, x] = pixel

    plt.imshow(new_row_array)
    plt.show()

    return new_row_array

def test(image_array, height, width, array_size):
     # New image frame
    new_row_array = np.zeros((height, width, array_size), dtype=np.uint8)
    mid_x = int(width/2)
    mid_y = int(height/2)

    for y in range(0, height, 1):
            for x in range(0, width, 1):
                pixel = intensity_level_slicing(image_array, x, y)
                new_row_array[y, x] = pixel


    plt.imshow(new_row_array)
    plt.show()

def plot_hist(new_image_arr, L):
    # Handle both numpy arrays and lists of pixels
    if isinstance(new_image_arr, np.ndarray):
        # If it's a numpy array (3D image), extract R channel
        gray_values = new_image_arr[:, :, 0]   # take R channel
        # Flatten to 1D for histogram
        gray_values = gray_values.flatten()
    else:
        # If it's a list of pixels, extract R channel (first element) from each pixel
        gray_values = np.array([pixel[0] for pixel in new_image_arr])

    # plt.hist(gray_values, bins=L, range=(0, L-1))
    # plt.xlabel("Pixel Intensity")
    # plt.ylabel("Frequency")
    # plt.show()

    # plt.hist(gray_values, bins=L, range=(0, L-1), density=True)
    # plt.xlabel("Pixel Intensity")
    # plt.ylabel("Probability Density")
    # plt.show()

    counts, bin_edges = np.histogram(
    gray_values,
    bins=L,
    range=(0, L-1)
    )

    # print(counts)
    # Normalised 
    # hist, bins = np.histogram(gray_values, bins=L, range=(0, L-1))
    # hist_norm = hist / hist.sum()  # sums to 1
    # plt.bar(bins[:-1], hist_norm, width=1)
    # plt.xlabel("Pixel Intensity")
    # plt.ylabel("Probability")
    # plt.show()

    return counts, gray_values

def global_hist_equalisation(counts, hist_vals, new_image_arr, L):
    height, width, pixel_array_size = new_image_arr.shape
    hist_row_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
 
    # MN = 889
    MN = len(new_image_arr)

    CDF = np.zeros(len(counts))
    p_r = np.zeros(len(counts))

    for i in range(0, len(counts)):
        p_r[i] = counts[i] / MN

    for i in range(0, len(p_r)):
        if i == 0:
            CDF[0] = p_r[0]
        else:
            CDF[i] = p_r[i] + CDF[i-1]

    CDF = (L-1) * CDF
    # print(CDF)

    # Rounded
    s = [int(round(p)) for p in CDF]  # take R channel

    print(s)

    for y in range(0, height, 1):
        for x in range(0, width, 1):
            pixel = new_image_arr[y, x]
            replace_val = pixel[0] - 1 
            hist_row_array[y, x] = s[replace_val]

            if hist_row_array[y, x].ndim == 0:  # grayscale pixel
                hist_row_array[y, x] = np.uint8(np.clip(s, 0, 255))
            else:  # color pixel (length-3 array)
                hist_row_array[y, x] = np.clip(hist_row_array[y, x], 0, 255).astype(np.uint8)

    plt.imshow(hist_row_array)
    plt.show()

def local_hist_equalisation(new_image_arr, L, m):
    height, width, pixel_array_size = new_image_arr.shape
    hist_row_array = np.zeros((height, width, pixel_array_size), dtype=np.uint8)
    
    for y in range(0, height, 1):
        for x in range(0, width, 1):
            num_pixels = 0
            p_array = []

            # for y_m in range(0, m, 1):
            #     for x_m in range(0, m, 1):
            #         check = clamp_vals((x + x_m), (y + y_m), width, height)
            #         if check == True:
            #             p_array.append(new_image_arr[(y + y_m), (x + x_m)])
            #             num_pixels += 1

            # Get surrounding co-ordinates
            pixel = new_image_arr[y, x]
            p_array.append(pixel)
            num_pixels += 1

            # Get up co-ordinate
            x_up = x
            y_up = y - 1
            check = clamp_vals(x_up, y_up, width, height)
            if check == True:
                p_array.append(new_image_arr[y_up, x_up])
                num_pixels += 1

            # Get up right co-ordinate
            x_up_right = x + 1
            y_up_right = y - 1
            check = clamp_vals(x_up_right, y_up_right, width, height)
            if check == True:
                p_array.append(new_image_arr[y_up_right, x_up_right])
                num_pixels += 1
            
            # Get right co-ordinate
            x_right = x + 1
            y_right = y
            check = clamp_vals(x_right, y_right, width, height)
            if check == True:
                p_array.append(new_image_arr[y_right, x_right])
                num_pixels += 1

            # Get right down co-ordinate
            x_down_right = x + 1
            y_down_right = y + 1
            check = clamp_vals(x_down_right, y_down_right, width, height)
            if check == True:
                p_array.append(new_image_arr[y_down_right, x_down_right])
                num_pixels += 1

            # Get down co-ordinate
            x_down = x
            y_down = y + 1
            check = clamp_vals(x_down, y_down, width, height)
            if check == True:
                p_array.append(new_image_arr[y_down, x_down])
                num_pixels += 1

            # Get down left co-ordinate
            x_down_left = x - 1
            y_down_left = y + 1
            check = clamp_vals(x_down_left, y_down_left, width, height)
            if check == True:
                p_array.append(new_image_arr[y_down_left, x_down_left])
                num_pixels += 1

            # Get left co-ordinate
            x_left = x - 1
            y_left = y 
            check = clamp_vals(x_left, y_left, width, height)
            if check == True:
                p_array.append(new_image_arr[y_left, x_left])
                num_pixels += 1

            # Get left up co-ordinate
            x_up_left = x - 1
            y_up_left = y - 1
            check = clamp_vals(x_up_left, y_up_left, width, height)
            if check == True:
                p_array.append(new_image_arr[y_up_left, x_up_left])
                num_pixels += 1

            s = get_pixels(p_array, num_pixels, L)

            pixel = new_image_arr[y, x]
            replace_val = pixel[0] 
            hist_row_array[y, x] = s[replace_val]

            if hist_row_array[y, x].ndim == 0:  # grayscale pixel
                hist_row_array[y, x] = np.uint8(np.clip(s, 0, 255))
            else:  # color pixel (length-3 array)
                hist_row_array[y, x] = np.clip(hist_row_array[y, x], 0, 255).astype(np.uint8)
 
            # print(hist_row_array[y, x])

    # plt.imshow(hist_row_array)
    # plt.show()
    return hist_row_array

def clamp_vals(x_test, y_test, width, height):
    # if x_test > width:
    #     return False
    # if x_test < 0:
    #     return False
    # if y_test > height:
    #     return False
    # if y_test < 0:
    #     return False
    # else:
    #     return True

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

def get_pixels(array_region, num_pixels, L):
    counts, hist_vals = plot_hist(array_region, L)
    MN = num_pixels

    CDF = np.zeros(len(counts))
    p_r = np.zeros(len(counts))

    for i in range(0, len(counts)):
        p_r[i] = counts[i] / MN

    # print(p_r)

    for i in range(0, len(p_r)):
        if i == 0:
            CDF[0] = p_r[0]
        else:
            CDF[i] = p_r[i] + CDF[i-1]

    CDF = (L-1) * CDF

    # print(CDF)

    # Rounded
    s = [int(round(p)) for p in CDF]  # take R channel

    return s

def main():
    # # Small image sample
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

    transform_type =  None# "light_dark" # "contrast" # "intense_slicing" # "gamma" # "log" #
    histogram =   "local_hist_equal" # "global_hist_equal" # hist 

    match transform_type:
        case "log":
            image_path = 'Figures/fourier_spectrum.png' 
            new_image_arr = transform_image(image_path, transform_type)

        case "gamma":
            image_path = 'Figures/intensity_ramp.png' 
            new_image_arr = transform_image(image_path, transform_type)

        case "contrast":
            image_path = 'Figures/contrast_stretching.png' 
            new_image_arr = transform_image(image_path, transform_type)

        case "intense_slicing":
            image_path = 'Figures/intensity_level.png' 
            new_image_arr = transform_image(image_path, transform_type)

        case "light_dark":
            image_path = 'Figures/contrast_stretching.png' 
            new_image_arr = transform_image(image_path, transform_type)
        
        case None:
            print("No transformation")

    match histogram:
        case "basic":
            L = 256
            counts, hist_vals = plot_hist(new_image_arr, L)

        case "global_hist_equal":
            L = 256 # no. levels
            counts, hist_vals = plot_hist(new_image_arr, L)
            global_hist_equalisation(counts, hist_vals, new_image_arr, L)

            # Library
            # equ = cv2.equalizeHist(new_image_arr[:, :, 0])

            # # Create figure and axis
            # fig, ax = plt.subplots()

            # # Add labels
            # ax.set_xlabel("X Pixel Coordinate")
            # ax.set_ylabel("Y Pixel Coordinate")

            # # Save
            # save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
            # fig.savefig(f"{save_path}intensity_hist_global.pdf", bbox_inches="tight")
            # plt.close(fig)

        case "local_hist_equal":
            L = 256 # no. levels
            m = 3
            image_path = 'Figures/local_histogram_processing.png'
            image_array = cv2.imread(image_path)

            # Create figure and axis
            fig, ax = plt.subplots()

            ax.imshow(image_array)

            # Add labels
            ax.set_xlabel("X Pixel Coordinate")
            ax.set_ylabel("Y Pixel Coordinate")

            # Save
            save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
            fig.savefig(f"{save_path}intensity_hist_local_orig.pdf", bbox_inches="tight")
            plt.close(fig)

            # Plot image
            plt.imshow(image_array, cmap='gray')
            plt.show()

            output_array = local_hist_equalisation(image_array, L, m)

            # Create figure and axis
            fig, ax = plt.subplots()

            ax.imshow(output_array)

            # Add labels
            ax.set_xlabel("X Pixel Coordinate")
            ax.set_ylabel("Y Pixel Coordinate")

            # Save
            save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
            fig.savefig(f"{save_path}intensity_hist_local.pdf", bbox_inches="tight")
            plt.close(fig)

if __name__ == "__main__":
    main()
