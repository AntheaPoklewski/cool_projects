import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math
from skimage.color import rgb2luv
from skimage.color import rgb2lab
from skimage import io
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix,  diags
from scipy.sparse.linalg import eigsh
from sklearn.datasets import make_blobs
from skimage import data, segmentation, color, graph
from skimage.transform import resize

# Complete normalized cut segmentation pipeline
    
#     Args:
#         image: Input RGB image (H×W×3, values 0-255)
#         sigma_I: Color similarity bandwidth
#         sigma_X: Spatial proximity bandwidth
#         r: Spatial connection radius
#         num_segments: Number of segments (currently supports 2)
    
#     Returns:
#         labels: Segmentation labels (H×W)
#         segmented_image: Segmented image

def build_weight_matrix(image, sigma_I=0.1, sigma_X=4.0, r=5):
    image_lab = rgb2lab(image / 255.0)
    height, width = image.shape[:2]
    n_pixels = height * width
    
    # Store sparse matrix in COO format
    rows = []
    cols = []
    data = []

    for i in range(height):
        for j in range(width):
            idx1 = i * width + j
            # Position and color of pixel (i,j)
            pos1 = np.array([i, j])
            color1 = image_lab[i, j]

            for di in range(-r, r+1):
                for dj in range(-r, r+1):
                    ni, nj = i + di, j + dj

                    # Check bounds
                    if ni < 0 or ni >= height or nj < 0 or nj >= width:
                        continue

                    idx2 = ni * width + nj
                    if idx1 == idx2:
                        continue

                    # Position and color of neighbor
                    pos2 = np.array([ni, nj])
                    color2 = image_lab[ni, nj]

                    # Compute distances
                    spatial_dist = np.linalg.norm(pos1 - pos2)

                    # Only connect if within radius
                    if spatial_dist <= r:
                        color_dist = np.linalg.norm(color1 - color2)

                        # Compute weight (product of two Gaussians)
                        w = np.exp(-color_dist**2 / (2 * sigma_I**2)) * \
                            np.exp(-spatial_dist**2 / (2 * sigma_X**2))
                        
                        rows.append(idx1)
                        cols.append(idx2)
                        data.append(w)

    # Create sparse matrix
    W = csr_matrix((data, (rows, cols)), shape=(n_pixels, n_pixels))
    
    # Make symmetric
    W = (W + W.T) / 2
    
    return W

def compute_normalized_laplacian(W):

    # Degree vector
    D = np.array(W.sum(axis=1)).flatten()
    
    # FIX 4: Add small epsilon to all degrees
    # Prevents division by zero AND near-singular matrices
    epsilon = 1e-8
    D = D + epsilon
    
    # D^(-1/2)
    D_inv_sqrt = 1.0 / np.sqrt(D)
    
    # Create sparse diagonal matrices
    D_inv_sqrt_sparse = diags(D_inv_sqrt)
    D_sparse = diags(D)
    
    # Normalized Laplacian: D^(-1/2) (D - W) D^(-1/2)
    # = I - D^(-1/2) W D^(-1/2)
    n = W.shape[0]
    I = diags(np.ones(n))
    
    # D^(-1/2) W D^(-1/2)
    D_inv_sqrt_W = D_inv_sqrt_sparse @ W @ D_inv_sqrt_sparse
    
    L_norm = I - D_inv_sqrt_W
    
    return L_norm, D, D_inv_sqrt

def compute_ncut_eigenvectors(W, num_eigenvectors = 2):
    D = np.array(W.sum(axis=1)).flatten()
    D_sparse = csr_matrix(np.diag(D))
    D_sqrt_inv = np.sqrt(1.0 / (D + 1e-10)) 
    L = D_sparse - W
    n = W.shape[0]
    k = min(num_eigenvectors + 2, n - 1)
    L_norm, D, D_inv_sqrt = compute_normalized_laplacian(W)
    
    eigenvalues, eigenvectors = eigsh(
        L_norm,
        k=k,
        sigma=1e-6,      # Slight shift away from 0
        which='LM',       # Largest magnitude near sigma
        tol=1e-6,         # Tolerance
        maxiter=2000      # More iterations
    )

    # Sort by eigenvalue
    idx = eigenvalues.argsort()
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Skip first eigenvector (constant, eigenvalue=0)
    return eigenvalues[1:], eigenvectors[:, 1:]

def partition_from_eigenvector(eigenvector, method="median"):
    if method == 'median':
        threshold = np.median(eigenvector)
    elif method == 'zero':
        threshold = 0
    elif method == 'optimal':
        # Search for best threshold
        threshold = find_optimal_threshold(eigenvector)
    else:
        threshold = 0
    
    labels = (eigenvector > threshold).astype(int)
    
    return labels

def find_optimal_threshold(eigenvector, num_splits=100):
    # Try different thresholds
    min_val, max_val = eigenvector.min(), eigenvector.max()
    thresholds = np.linspace(min_val, max_val, num_splits)
    
    # For simplicity, just use median
    # Full implementation would compute Ncut for each threshold
    return np.median(eigenvector)

def create_segmented_image(image, labels):
    segmented = np.zeros_like(image)
    for label in np.unique(labels):
        mask = labels == label
        mean_color = image[mask].mean(axis=0)
        segmented[mask] = mean_color
    return segmented

def normalized_cut_segmentation(image, sigma_I=0.1, sigma_X=4.0, r=5, num_segments=2):
    height, width = image.shape[:2]
    W = build_weight_matrix(image, sigma_I, sigma_X, r)
    _, eigenvectors = compute_ncut_eigenvectors(W, num_eigenvectors=1)

    second_eigenvector = eigenvectors[:, 0]
    labels_1d = partition_from_eigenvector(second_eigenvector, method='median')
    labels = labels_1d.reshape(height, width)
    segmented_image = create_segmented_image(image, labels)
    
    return labels, segmented_image

def save_image(image_info, q):
    # Create figure and axis
    # Create figure and axis
    fig, ax = plt.subplots()

    ax.imshow(image_info)

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}norm_cut_{q}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    # image = np.zeros((100, 100, 3), dtype=np.uint8)
    # image[:, :50] = [255, 0, 0]  # Red left half
    # image[:, 50:] = [0, 0, 255]  # Blue right half
    
    # # Add noise
    # noise = np.random.randint(-20, 20, image.shape)
    # image = np.clip(image.astype(int) + noise, 0, 255).astype(np.uint8)

    # Second red region (bottom-right 3x3 square)
    image_path = 'Figures/mean_shift_clustering.png' 
    image = cv2.imread(image_path)
    save_image(image, "orig")

    scale = 0.25
    new_shape = (int(image.shape[0] * scale), int(image.shape[1] * scale))
    image_small = (resize(image, new_shape, anti_aliasing=True) * 255).astype(np.uint8)
    
    # Plot image
    plt.imshow(image_small)
    plt.show()

    labels, segmented = normalized_cut_segmentation(image_small, sigma_I=0.1, sigma_X=4.0, r=5)
    plt.imshow(segmented)
    plt.show()
    # save_image(segmented, "orig") 

    # Using a library:
    img = image
    labels1 = segmentation.slic(img, compactness=30, n_segments=400, start_label=1)
    out1 = color.label2rgb(labels1, img, kind='avg', bg_label=0)

    g = graph.rag_mean_color(img, labels1, mode='similarity')
    labels2 = graph.cut_normalized(labels1, g)
    out2 = color.label2rgb(labels2, img, kind='avg', bg_label=0)

    # fig, ax = plt.subplots()

    # ax[0].imshow(out1)
    # ax[1].imshow(out2)

    # for a in ax:
    #     a.axis('off')

    # plt.tight_layout()
    # plt.show()
    save_image(out2, "norm_cut")

if __name__ == "__main__":
    main()