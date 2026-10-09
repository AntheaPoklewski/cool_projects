import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math
from skimage.color import rgb2luv
from scipy.spatial.distance import cdist
from sklearn.datasets import make_blobs
 
# Image segmentation using mean shift in joint spatial-color domain.
# Based on Section 4.2.1 of the paper.

# Args:
#     image: H × W × 3 RGB image (values 0-255)
#     spatial_bandwidth: h_s (spatial resolution)
#     color_bandwidth: h_r (color resolution)
#     min_region_size: Minimum pixels per region

# Returns:
#     segmented_image: Segmented image
#     labels: Cluster label for each pixel


# h_s = spatial bandwidth
# h_r = colour_bandwidth

def gaussian_kernel(distance, bandwidth):
    return np.exp(-0.5 * (distance / bandwidth) ** 2)

def image_to_features(image):
    image_luv = rgb2luv(image / 255.0)
    height, width, pixel_array_size = image.shape
    n_pixels = height * width

    features = np.zeros((n_pixels, 5))
    idx = 0
    for i in range(0, height):
        for j in range(0, width):
            idx = i * width + j
            features[idx] = [i, j, image_luv[i, j, 0], image_luv[i, j, 1], image_luv[i, j, 2]]
            idx += 1

    return height, width, n_pixels, features

def create_grid_space(height, width, grid_size, features):
    grid_indices = []
    grid_features = []
    for i in range(0, height, grid_size):
        for j in range(0, width, grid_size):
            idx = i * width + j
            grid_features.append(features[idx])
            grid_indices.append(idx)
    
    grid_features = np.array(grid_features)

    return grid_features, grid_indices

def mean_shift_filter(features, h_s, h_r, max_iter=100, tol=0.1):
    n_points = features.shape[0]
    modes = np.zeros_like(features)

    for i in range(n_points):
        mode = mean_shift_filter_point(features[i], features, h_s, h_r, max_iter, tol)
        modes[i] = mode

    return modes

def mean_shift_filter_point(start_point, features, h_s, h_r, max_iter=100, tol=0.1):
    current = start_point.copy()

    for iteration in range(max_iter): # usually converges between 5-30 iterations -> safety net
        new_point, shift = mean_shift_step(current, features, h_s, h_r)
        if shift < 0.1: # small tolerance
                break

        current = new_point

    return current

def mean_shift_step(current_point, features, h_s, h_r):
    spatial_current = current_point[:2]
    color_current = current_point[2:]

    spatial_features = features[:, :2]
    color_features = features[:, 2:]

    spatial_distance = np.linalg.norm(spatial_features - spatial_current[:2], axis=1) # calculate distance from current point to each data point
    colour_distance = np.linalg.norm(color_features - color_current[2:], axis = 1) # calculate colour distance from current point to each data point

    spatial_weights = gaussian_kernel(spatial_distance, h_s)
    color_weights = gaussian_kernel(colour_distance, h_r)

    weights = spatial_weights * color_weights

    weight_sum = np.sum(weights)
    if weight_sum == 0:
        return current_point, 0
    
    weights = weights/weight_sum # calc average
    new_point = np.sum(features * weights[:, np.newaxis], axis = 0)

    # check converegence
    shift = np.linalg.norm(new_point - current_point)

    return current_point, shift

def delineate_clusters(modes, h_s, h_r):
    # Delineate clusters by grouping pixels with similar modes
    #Delineate the clusters by grouping together all data points that are closer than h_s in spatial domain and h_r in range domain
    n_points = modes.shape[0]
    labels = -np.ones(n_points, dtype=int)
    cluster_centers = []
    cluster_id = 0

    for i in range(n_points):
        if labels[i] == -1:
            spatial_diff = np.linalg.norm(modes[:, :2] - modes[i, :2], axis = 1)
            colour_diff = np.linalg.norm(modes[:, 2:] - modes[i, 2:], axis = 1)

        similar_mask = (spatial_diff < h_s) & (colour_diff < h_r)

        labels[similar_mask] = cluster_id
        cluster_centers.append(modes[i])
        cluster_id += 1
    
    return labels, np.array(cluster_centers)

def create_segmented_image(original_image, labels, height, width):
    segmented = np.zeros_like(original_image)
    labels_2d = labels.reshape(height, width)
    
    for label in np.unique(labels):
        mask = labels_2d == label
        mean_color = original_image[mask].mean(axis=0)
        segmented[mask] = mean_color
    
    return segmented

def mean_shift_image_segment(image, h_s, h_r, min_region_size=20, grid_size=20):
    features = []
    height, width, _, features = image_to_features(image)
    grid_features, _ = create_grid_space(height, width, grid_size, features)
    modes_grid = mean_shift_filter(grid_features, h_s, h_r)
    
    modes = np.zeros_like(features)
    for i, feature in enumerate(features):
        # Find nearest grid mode
        distances = np.linalg.norm(grid_features - feature, axis=1)
        nearest = np.argmin(distances)
        modes[i] = modes_grid[nearest]

    labels, _ = delineate_clusters(modes, h_s, h_r)
    segmented_image = create_segmented_image(image, labels, height, width)

    # Reshape labels to 2D
    labels_2d = labels.reshape(height, width)
    n_clusters = len(np.unique(labels))
    
    return segmented_image, labels_2d, n_clusters

def save_image(image_info, q):
    # Create figure and axis
    # Create figure and axis
    fig, ax = plt.subplots()

    ax.imshow(image_info, cmap="grey")

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}mean_shift_{q}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    # # Image size
    # H, W = 200, 200

    # # Create coordinate grid
    # y, x = np.mgrid[0:H, 0:W]

    # # Define blob centers
    # # Blob centers and colours
    # blobs = [
    #     (60, 60,  (1, 0, 0)),   # Red blob
    #     (140, 80, (0, 1, 0)),   # Green blob
    #     (100, 150,(0, 0, 1))    # Blue blob
    # ]

    # # Create empty image
    # image = np.zeros((H, W, 3), dtype=float)
    # sigma = 20

    # # Add coloured Gaussian blobs
    # for cy, cx, colour in blobs:
    #     gaussian = np.exp(-((x - cx)**2 + (y - cy)**2) / (2 * sigma**2))
    
    # for c in range(3):
    #     image[..., c] += gaussian * colour[c]

    # # Normalize to 0–255
    # image = image / image.max()
    # image = (255 * image).astype(np.uint8)

    # plt.imshow(image)
    # plt.show()

    # Second red region (bottom-right 3x3 square)
    image_path = 'Figures/mean_shift_clustering.png' 
    image = cv2.imread(image_path)
    
    # Plot image
    plt.imshow(image)
    plt.show()
    save_image(image, "orig")

    #h_s -> 5-15
    #h_r -> 5-28

    s_bw = 8
    c_bw = 8

    segmented, labels, clusters = mean_shift_image_segment(image, s_bw, c_bw, min_region_size=20)
    plt.imshow(segmented)
    plt.show()
    save_image(segmented, "segmented")

if __name__ == "__main__":
    main()