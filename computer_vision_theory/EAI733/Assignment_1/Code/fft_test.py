import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math

def norm(image):
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def create_2d_gaussian_filter(P, Q, sigma):
    """
    Create 2D Gaussian filter in frequency domain
    
    shape: (height, width)
    sigma: controls cutoff frequency
    """
    rows, cols = P, Q
    crow, ccol = rows // 2, cols // 2
    
    # Create coordinate grids
    y, x = np.ogrid[:rows, :cols]
    
    # Distance from center
    distance_squared = (x - ccol)**2 + (y - crow)**2
    
    # 2D Gaussian filter
    gaussian = np.exp(-distance_squared / (2 * sigma**2))
    
    return gaussian

def main():
    image_path = 'Figures/FFT.png' 
    image_array = cv2.imread(image_path)
    height, width,_ = image_array.shape

    array_vals = image_array[:, :, 0]
    plt.imshow(array_vals, cmap='gray')
    plt.show()

    P, Q = 2 * height, 2 * width
    fp = np.zeros((P, Q))
    fp[:height, :width] = array_vals

    y, x = np.indices((P, Q))
    centering_mask = np.power(-1, x + y)
    fp_centered = fp * centering_mask

    fft_result = np.fft.fft2(fp_centered)

    spec_mag = np.log(1 + np.abs(fft_result))
    image_result = norm(spec_mag)
    plt.imshow(image_result, cmap='gray')
    plt.show()

    # Gaussian filter
    sigma = 30
    H = create_2d_gaussian_filter(P, Q, sigma)
    G_freq = fft_result * H
    g_spec_mag = np.log(1 + np.abs(G_freq))
    image_result = norm(g_spec_mag)
    plt.imshow(image_result, cmap='gray')
    plt.show()

    # Inverse
    gp_centered = np.real(np.fft.ifft2(G_freq))
    gp = gp_centered * centering_mask
    image_result = norm(gp)
    plt.imshow(image_result, cmap='gray')
    plt.show()

    g = gp[:height, :width]
    image_result = norm(g)
    plt.imshow(image_result, cmap='gray')
    plt.show()


if __name__ == "__main__":
    main()