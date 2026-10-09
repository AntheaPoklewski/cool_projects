import numpy as np
import cv2
from sklearn.mixture import GaussianMixture
from skimage import color, filters, io
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
from skimage.transform import resize
from scipy.ndimage import convolve
from scipy.ndimage import maximum_filter
from skimage import data, color

def select_detector(detector_type):
    match detector_type:
        case "moravec":
            # Detect corners
            image_path = 'Assignment_1/Figures/moravec_building.jpg' 
            image, height, width = prep_image(image_path, detector_type)
            corners, response = moravec_corner_detect(image, height, width, window_size=5, threshold=500, )
            
            # Visualize
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))

            axes[0].imshow(image, cmap='gray')
            axes[0].set_title('Original Image')
            axes[0].axis('off')

            axes[1].imshow(response, cmap='hot')
            axes[1].set_title('Moravec Response')
            axes[1].axis('off')

            # axes[2].imshow(image, cmap='gray')
            # y_coords, x_coords = np.where(corners)
            # axes[2].plot(x_coords, y_coords, 'r.', markersize=5)
            # axes[2].set_title('Detected Corners')
            # axes[2].axis('off')

            plt.tight_layout()
            plt.show()

        case "harris":
            image_path = 'Assignment_1/Figures/moravec_building.jpg' 
            image, height, width = prep_image(image_path, detector_type)
            corners, response, edges = harris_corner_detect(image, height, width, sigma=1.0, k=0.04, threshold=0.01, window_size=3)
            
            # Visualize
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))

            axes[0].imshow(image, cmap='gray')
            axes[0].set_title('Original Image')
            axes[0].axis('off')

            axes[1].imshow(response, cmap='gray')
            axes[1].set_title('Harris Response')
            axes[1].axis('off')

            # axes[2].imshow(image, cmap='gray')
            # y_coords, x_coords = np.where(corners)
            # axes[2].plot(x_coords, y_coords, 'r.', markersize=5)
            # axes[2].set_title('Detected Corners')
            # axes[2].axis('off')

            plt.tight_layout()
            plt.show()

    save_image(response, detector_type)

def prep_image(image_path, detector_type):
    image = cv2.imread(image_path)
    height, width,_ = image.shape
    # save_image(image, f"{detector_type}_original")

    image = (image * 255).astype(np.uint8)
    return image, height, width

def moravec_corner_detect(image, height, width, window_size=5, threshold=500 ):
    # height, width = 7, 7
    image_grey = image[:, :, 0]
    half_w = window_size // 2
    window = np.ones((window_size, window_size))

    shifts = [
        (1, 0), # Right
        (1, 1), # Diagonal down-right
        (0, 1), # Down
        (-1, 1) # Diagonal down-left
    ]

    convolve_result = np.zeros((len(shifts), height, width))

    for idx, (dx, dy) in enumerate(shifts):
        shifted = np.roll(image_grey, shift=(dy, dx), axis=(0,1))
        # print(shifted)
        diff_squared = (shifted.astype(float) - image_grey.astype(float)) ** 2
        # print(diff_squared)
        E = convolve(diff_squared, window, mode='constant', cval=0.0)
        # print(E)
        convolve_result[idx] = E
        # print(convolve_result)

    corner_response = np.min(convolve_result, axis=0)
    print(corner_response)
    local_max = maximum_filter(corner_response, size=3)
    corners = (corner_response == local_max) & (corner_response > threshold)
    return corners, corner_response

def harris_corner_detect(image_rgb, height, width, sigma=1.0, k=0.04, threshold=0.01, window_size=3):
    image = image_rgb[:, :, 0]

    # Ensure float image
    if image.max() > 1.0:
        image = image.astype(float) / 255.0
    else:
        image = image.astype(float)

    Ix = convolve(image, np.array([[-1, 0, 1]]), mode='constant')
    Iy = convolve(image, np.array([[-1], [0], [1]]), mode='constant')
    
    Ixx = Ix * Ix
    Iyy = Iy * Iy
    Ixy = Ix * Iy

    A = gaussian_filter(Ixx, sigma=sigma)  # Smoothed Ix²
    B = gaussian_filter(Iyy, sigma=sigma)  # Smoothed Iy²
    C = gaussian_filter(Ixy, sigma=sigma)  # Smoothed Ix·Iy

    det_M = A * B - C * C           # Determinant: λ₁·λ₂
    trace_M = A + B                  # Trace: λ₁ + λ₂
    
    response = det_M - k * (trace_M ** 2)

    # Corner detection (R > 0)
    corner_threshold = threshold * response.max()
    corner_candidates = response > corner_threshold

    local_max = maximum_filter(response, size=window_size)
    corners = (response == local_max) & corner_candidates

    # Edge detection (R < 0)
    # Edges have negative response
    edge_response = -response  # Flip sign so edges are positive
    edge_threshold = threshold * edge_response.max()
    edge_candidates = edge_response > edge_threshold
    
    # Thin edges: non-maximum suppression along gradient direction
    # Check if local minimum in x or y direction based on gradient magnitude
    gradient_mag = np.sqrt(Ix**2 + Iy**2)
    
    # Simple edge thinning: local minima of response
    local_min_x = np.zeros_like(response, dtype=bool)
    local_min_y = np.zeros_like(response, dtype=bool)
    
    # Check if response is local minimum along x
    for i in range(1, response.shape[0]-1):
        for j in range(1, response.shape[1]-1):
            if np.abs(Ix[i, j]) > np.abs(Iy[i, j]):
                # Dominant gradient in x, check x direction
                if response[i, j] <= response[i, j-1] and \
                   response[i, j] <= response[i, j+1]:
                    local_min_x[i, j] = True
            else:
                # Dominant gradient in y, check y direction
                if response[i, j] <= response[i-1, j] and \
                   response[i, j] <= response[i+1, j]:
                    local_min_y[i, j] = True
    
    edges = (local_min_x | local_min_y) & edge_candidates
    
    return corners, response, edges
        
def save_image(image_info, q):
    fig, ax = plt.subplots()

    # ax.imshow(image_info, cmap='gray')
    ax.imshow(image_info, cmap='gray')

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}detectors_{q}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    # Load image
    # Simple 7×7 image with a corner
    # image = np.array([
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    # ], dtype=float)

    detector_type =  "harris" # "moravec" # 
    select_detector(detector_type)

if __name__ == "__main__":
    main()