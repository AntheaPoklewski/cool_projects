import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math

# Question 5 -> image rescaling (showing aliasing) -> a) compensate by first applying 3x3 averaging filter then resize b) apply FFT method

def resize_nearest_neighbor(image, new_height, new_width):
    """
    Resize image using nearest neighbor interpolation
    This is the simplest method - just picks the closest pixel
    """
    old_height, old_width = image.shape[:2]
    is_rgb = len(image.shape) == 3
    
    # Create output array
    if is_rgb:
        resized = np.zeros((new_height, new_width, 3), dtype=image.dtype)
    else:
        resized = np.zeros((new_height, new_width), dtype=image.dtype)
    
    # Calculate scaling factors
    row_scale = old_height / new_height
    col_scale = old_width / new_width
    
    # For each pixel in the output image
    for i in range(new_height):
        for j in range(new_width):
            # Map to source coordinates
            src_i = int(i * row_scale)
            src_j = int(j * col_scale)
            
            # Clamp to valid range
            src_i = min(src_i, old_height - 1)
            src_j = min(src_j, old_width - 1)
            
            # Copy pixel value
            resized[i, j] = image[src_i, src_j]
    
    return resized

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

def gaussian_lowpass_filter(image, sigma):
    rows, cols = image.shape[:2]
    crow, ccol = rows // 2, cols // 2 # get center 
    y, x = np.ogrid[:rows, :cols]
    distance_squared = (x - ccol)**2 + (y - crow)**2
    gaussian_filter = np.exp(-distance_squared / (2 * sigma**2))
    f_transform = np.fft.fft2(image[:, :, 0])
    f_shift = np.fft.fftshift(f_transform)
    f_filtered = f_shift * gaussian_filter
    f_ishift = np.fft.ifftshift(f_filtered)
    filtered = np.abs(np.fft.ifft2(f_ishift))
    
    return filtered

def shift_array(array_region, height, width): 
    f_shift = np.zeros((height, width, 1), dtype=np.uint8)
    x_array = np.arange(width).reshape(-1, 1)
    y_array = np.arange(height).reshape(-1, 1)
    # f_complex = np.complex128(array_region)
    for y in y_array:
        for x in x_array:
            f_shift[y, x] = np.uint8(np.clip(array_region[y, x] * ((-1) ** (x+y)), 0, 255))

    return f_shift

    # Euler's expression e^(j*theta) = cos(theta)+jsin(theta)
    # (-1)^(x+y) = e^(j*pi*(x+y))

def FFT_first_principles(image):
    """
    Compute a 2D FFT from first principles using a separable 1D FFT.

    This implementation:
    - Works on a single-channel (grayscale) 2D array
    - Assumes each dimension is a power of 2
    - Matches the unnormalised definition used by np.fft.fft2
    """
    # Ensure complex type
    image = np.asarray(image, dtype=complex)

    # If an image with channels is passed (H, W, C), take the first channel
    if image.ndim == 3:
        image = image[:, :, 0]

    rows, cols = image.shape
    result = image.copy()

    # 2D DFT: X[k,l] = ΣΣ x[m,n] · e^(-2πi(km/M + ln/N))
    # Key insight: This can be separated into:
    # 1. FFT along each row (fixing m, varying n)
    # 2. FFT along each column (fixing n, varying m)
    
    # This has time complexity O(n^2) which means it becomes infintely more complex
    # for u in range(height):
    #     for v in range(width):
    #         for y in range(height):
    #             for x in range(width):
    #                 F[u, v] += f[y, x]*np.exp(-2j*np.pi*(u*x/height + v*y/width))

    # rows_fft = np.zeros_like(x, dtype=complex)
    # for i in range(x.shape[0]):
    #     rows_fft[i, :] = perform_FFT(x[i, :])

    # cols_fft = np.zeros_like(rows_fft, dtype=complex)
    # for j in range(x.shape[1]):
    #     cols_fft[:, j] = perform_FFT(rows_fft[:, j])

    # 1D FFT along rows
    for i in range(rows):
        # Work on a copy of the row to avoid any weird view/stride issues
        result[i, :] = perform_fft_1d(result[i, :].copy())

    # 1D FFT along columns
    for j in range(cols):
        result[:, j] = perform_fft_1d(result[:, j].copy())

    return result

def perform_fft_1d(x):
    x = np.asarray(x, dtype=complex)
    N = len(x)
    # Require power-of-two length
    if N & (N - 1) != 0:
        raise ValueError("Length of input to perform_fft_1d must be a power of 2")
    # Bit-reversal
    bits = int(np.log2(N))
    for i in range(N):
        j = int(bin(i)[2:].zfill(bits)[::-1], 2)
        if i < j:
            x[i], x[j] = x[j], x[i]
    
    # Butterfly stages
    m = 2
    while m <= N:
        wm = np.exp(-2j * np.pi / m)
        for k in range(0, N, m):
            w = 1
            for j in range(m // 2):
                idx_top = k + j
                idx_bot = k + j + m // 2
                
                t = w * x[idx_bot]
                u = x[idx_top]
                
                x[idx_top] = u + t
                x[idx_bot] = u - t
                
                w *= wm
        m *= 2
    return x

def perform_FFT(x):
    N = len(x)
    if N & (N - 1) != 0:
        raise ValueError("N must be power of 2")
    
    bits = int(np.log2(N))
    for i in range(N):
        j = bit_reverse(i, bits)
        if i < j:
            x[i], x[j] = x[j], x[i]

    stage = 1
    length = 2

    while length <= N:
        # Twiddle factor for this stage
        angle = -2j * np.pi / length
        w = np.exp(angle)
        
        # Process all blocks of this size
        for start in range(0, N, length):
            wn = 1
            for k in range(length // 2):
                # Butterfly operation
                a_idx = start + k
                b_idx = start + k + length // 2
                
                a = x[a_idx]
                b = x[b_idx]
                
                t = wn * b
                x[a_idx] = a + t
                x[b_idx] = a - t
                
                wn *= w

        stage += 1
        length *= 2

    return x
    
def bit_reverse(n, bits):
    # """Reverse the bits of n"""
    result = 0
    for i in range(bits):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result

    # # Example
    # print("="*60)
    # x = [1, 2, 3, 4, 5, 6, 7, 8]
    # result = fft_iterative_explained(x.copy())
    # print("="*60)
    # print(f"Final result: {result}")
    # ```

    # ## **7. Understanding Bit Reversal**

    # The bit-reversal step reorders the input to match the recursive decomposition:
    # ```
    # N=8 example:

    # Index (binary) → Reversed → New Index
    # 0 (000)        → 000      → 0
    # 1 (001)        → 100      → 4
    # 2 (010)        → 010      → 2
    # 3 (011)        → 110      → 6
    # 4 (100)        → 001      → 1
    # 5 (101)        → 101      → 5
    # 6 (110)        → 011      → 3
    # 7 (111)        → 111      → 7

    # Original: [x₀, x₁, x₂, x₃, x₄, x₅, x₆, x₇]
    # Reordered: [x₀, x₄, x₂, x₆, x₁, x₅, x₃, x₇]

    # This matches the order from recursive splits

def resize_image_padding(image_array, height, width, ratio):
    P = height * ratio
    Q = width * ratio
    # padded_image_array = np.zeros((P, Q, 1), dtype=np.uint8)

    # for y in range(0, P):
    #     for x in range(0, Q):
    #         if (x < width and y < height):
    #             padded_image_array[y][x] = np.uint8(np.clip(image_array[y][x], 0, 255))
    #         # else:
    #         #     padded_image_array[i][j].append(np.uint(0)) # <- redundant

    # Find factor of 2
    # P = 2 ** int(np.ceil(np.log2(height)))
    # Q = 2 ** int(np.ceil(np.log2(width)))
    P = 2 * height
    Q = 2 * width

    padded_image_array = np.zeros((P, Q, 1), dtype=np.uint8)
    for y in range(0, P):
        for x in range(0, Q):
            if (x < width and y < height):
                padded_image_array[y][x] = np.uint8(np.clip(image_array[y][x], 0, 255))

    return padded_image_array, P ,Q

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

def highpass_filter(P, Q, d0, n):
    rows, cols = P, Q
    crow, ccol = rows // 2, cols // 2
    
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    
    # Avoid division by zero
    distance = np.where(distance == 0, 0.01, distance)
    
    # Butterworth high-pass
    butterworth = 1 - (1 / (1 + (d0 / distance)**(2 * n)))
    
    return butterworth
    
def lowpass_filter(P, Q, d0, n):
    rows, cols = P, Q
    crow, ccol = rows // 2, cols // 2
    
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    
    # Avoid division by zero
    distance = np.where(distance == 0, 0.01, distance)
    
    # Butterworth high-pass
    butterworth = 1 / (1 + (d0 / distance)**(2 * n))
    H = 1 / (1 + (d0 / distance)**(2 * n))
    
    return butterworth

def sobel_to_frequency(image_shape):
    """
    Convert Sobel kernels to frequency domain
    
    Key steps:
    1. Create Sobel kernels (3×3)
    2. Pad to image size
    3. Apply FFT
    4. Shift to center
    """
    
    # Step 1: Create Sobel kernels
    sobel_x = np.array([
        [-1,  0,  1],
        [-2,  0,  2],
        [-1,  0,  1]
    ], dtype=np.float64)
    
    sobel_y = np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float64)

    rows, cols = image_shape
    
    # Create padded kernels
    sobel_x_padded = np.zeros((rows, cols))
    sobel_y_padded = np.zeros((rows, cols))
    
    # Place 3×3 kernel at top-left
    sobel_x_padded[:3, :3] = sobel_x
    sobel_y_padded[:3, :3] = sobel_y
    
    # Step 3: Apply FFT
    sobel_x_freq = np.fft.fft2(sobel_x_padded)
    sobel_y_freq = np.fft.fft2(sobel_y_padded)

    # Step 4: Shift to center (for visualization)
    sobel_x_freq_shifted = np.fft.fftshift(sobel_x_freq)
    sobel_y_freq_shifted = np.fft.fftshift(sobel_y_freq)
    
    return {
        'sobel_x_freq': sobel_x_freq,
        'sobel_y_freq': sobel_y_freq,
        'sobel_x_freq_shifted': sobel_x_freq_shifted,
        'sobel_y_freq_shifted': sobel_y_freq_shifted
    }

def apply_sobel_frequency(image):
    """
    Apply Sobel filter in frequency domain
    
    This is equivalent to spatial domain convolution
    but can be faster for large images
    """
    
    # Handle RGB
    if len(image.shape) == 3:
        # Apply to each channel separately
        gx_total = np.zeros_like(image, dtype=np.float64)
        gy_total = np.zeros_like(image, dtype=np.float64)
        
        for c in range(3):
            gx, gy, mag, _ = apply_sobel_frequency(image[:, :, c])
            gx_total[:, :, c] = gx
            gy_total[:, :, c] = gy
        
        magnitude = np.sqrt(gx_total**2 + gy_total**2)
        direction = np.arctan2(gy_total, gx_total)
        
        return gx_total, gy_total, magnitude, direction
    
    # Step 1: Create Sobel kernels
    sobel_x = np.array([
        [-1,  0,  1],
        [-2,  0,  2],
        [-1,  0,  1]
    ], dtype=np.float64)
    
    sobel_y = np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float64)
    
    # Step 2: Pad kernels to image size
    rows, cols = image.shape
    sobel_x_padded = np.zeros((rows, cols))
    sobel_y_padded = np.zeros((rows, cols))
    sobel_x_padded[:3, :3] = sobel_x
    sobel_y_padded[:3, :3] = sobel_y
    
    # Step 3: FFT of image
    image_freq = np.fft.fft2(image)
    
    # Step 4: FFT of kernels
    sobel_x_freq = np.fft.fft2(sobel_x_padded)
    sobel_y_freq = np.fft.fft2(sobel_y_padded)
    
    # Step 5: Multiply in frequency domain (= convolution in spatial)
    gx_freq = image_freq * sobel_x_freq
    gy_freq = image_freq * sobel_y_freq
    
    # Step 6: Inverse FFT to get back to spatial domain
    gx = np.fft.ifft2(gx_freq).real
    gy = np.fft.ifft2(gy_freq).real
    
    # Step 7: Compute magnitude and direction
    magnitude = np.sqrt(gx**2 + gy**2)
    direction = np.arctan2(gy, gx)
    
    return gx, gy, magnitude, direction

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
    fig.savefig(f"{save_path}freq_domain_{q}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    question = "7" # "6b" # "6a" # "6_working" # "5b" # "5a" # "8" # 
    
    match question:
        case "5a":
            image_path = 'Figures/aliasing.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape
            plt.imshow(image_array)
            plt.show()
            save_image(image_array, "5a_orig")

            # resize_image(image_path, T_inv)
            aliased_image = resize_nearest_neighbor(image_array, round(height/2), round(width/2))
            plt.imshow(aliased_image)
            plt.show()
            save_image(aliased_image, "5a_aliased")

            average = uniform_neighbourhood_averaging(image_array, 3)
            plt.imshow(average)
            plt.show()
            save_image(average, "5a_average")

            no_aliasing = resize_nearest_neighbor(average, round(height/2), round(width/2))
            plt.imshow(no_aliasing)
            plt.show()
            save_image(no_aliasing, "5a_final")

        case "5b":
            image_path = 'Figures/aliasing.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape

            # resize_image(image_path, T_inv)
            aliased_image = resize_nearest_neighbor(image_array, round(height/2), round(width/2))
            plt.imshow(aliased_image)
            plt.show()
            
            sigma = 50
            gaussian_filter = gaussian_lowpass_filter(aliased_image, sigma)
            plt.imshow(gaussian_filter, cmap='gray')
            plt.show()
            save_image(aliased_image, "5b_gaussian")

            no_aliasing = resize_nearest_neighbor(gaussian_filter, round(height/2), round(width/2))
            plt.imshow(no_aliasing, cmap="grey")
            plt.show()
            save_image(aliased_image, "5b_final")

        case "6a":
            image_path = 'Figures/FFT.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape
            # plt.imshow(image_array, cmap='gray')
            # plt.show()

            ratio = 2
            is_h_pow2 = (height & (height - 1)) == 0
            is_w_pow2 = (width & (width - 1)) == 0

            # Using libraries ############################################
            # Apply 2D FFT
            
            # Pad to next power-of-two in *either* dimension if needed
            if not (is_h_pow2 and is_w_pow2):
                P = ratio * height
                Q = ratio * width
                image_array = np.pad(image_array[:, :, 0], ((0, P - height), (0, Q - width)), mode='constant')

            plt.imshow(image_array, cmap='gray')
            plt.show()

            # Shift zero frequency to center
            spectrum = np.fft.fft2(image_array)
            spectrum_shifted = np.fft.fftshift(spectrum)

            plt.imshow(np.abs(spectrum_shifted), cmap='gray')
            plt.show()
            
            # Compute magnitude spectrum
            magnitude = np.abs(spectrum_shifted)
            
            # Log scale for better visualization
            magnitude_log = np.log1p(magnitude)
            
            # Phase spectrum
            phase = np.angle(spectrum_shifted)

            magnitude_display = (magnitude_log / magnitude_log.max() * 255).astype(np.uint8)
            plt.imshow(magnitude_display, cmap='gray')
            plt.show()

            ############################################

        case "6b":
            image_path = 'Figures/FFT.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape
            # plt.imshow(image_array, cmap='gray')
            # plt.show()

            ratio = 2
            is_h_pow2 = (height & (height - 1)) == 0
            is_w_pow2 = (width & (width - 1)) == 0

            # Pad to the next power-of-two sizes for custom FFT as well
            if not (is_h_pow2 and is_w_pow2):
                image_array, height, width = resize_image_padding(image_array[:, :, 0], height, width, ratio)
                # plt.imshow(image_array, cmap='gray')
                # plt.show()

            shifted_array = shift_array(image_array, height, width)
            plt.imshow(shifted_array, cmap='gray')
            plt.show()
            save_image(shifted_array, "6_centered")

            # Our own 2D FFT (expects 2D grayscale or single-channel padded image)
            f_fft_spectrum = FFT_first_principles(shifted_array)
            spectrum_image = np.abs(f_fft_spectrum)

            # Enhance with log
            magnitude_log = np.log1p(spectrum_image)
            magnitude_display = (magnitude_log / magnitude_log.max() * 255).astype(np.uint8)

            phase = np.angle(f_fft_spectrum)

            plt.imshow(magnitude_display, cmap='gray')
            plt.show()

        case "6_working":
            image_path = 'Figures/FFT.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape

            array_vals = image_array[:, :, 0]
            plt.imshow(array_vals, cmap='gray')
            plt.show()
            save_image(array_vals, "6_orig")
            
            P, Q = 2 * height, 2 * width
            fp = np.zeros((P, Q))
            fp[:height, :width] = array_vals
            save_image(fp, "6_padded")

            y, x = np.indices((P, Q))
            centering_mask = np.power(-1, x + y)
            fp_centered = fp * centering_mask
            # plt.imshow(fp_centered, cmap='gray')
            # plt.show()
            
            fft_result = np.fft.fft2(fp_centered)

            spec_mag = np.log(1 + np.abs(fft_result))
            image_result = norm(spec_mag)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "6_fft_spectrum")

            # Gaussian filter
            sigma = 30
            H = create_2d_gaussian_filter(P, Q, sigma)
            save_image(H, "6_gaussian")

            G_freq = fft_result * H
            g_spec_mag = np.log(1 + np.abs(G_freq))
            image_result = norm(g_spec_mag)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "6_gaussian_result")

            # Inverse
            gp_centered = np.real(np.fft.ifft2(G_freq))
            gp = gp_centered * centering_mask
            image_result = norm(gp)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "6_ifft")

            g = gp[:height, :width]
            image_result = norm(g)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "6_final_cropped")
        
        case "7":
            image_path = 'Figures/equivalence_1.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape
            plt.imshow(image_array, cmap='gray')
            plt.show()
            save_image(image_array, "7_orig")
           
            y, x = np.indices((height, width))
            centering_mask = np.power(-1, x + y)
            fp_centered = image_array[:, :, 0] * centering_mask
            # plt.imshow(fp_centered, cmap='gray')
            # plt.show()
            
            fft_result = np.fft.fft2(fp_centered)

            spec_mag = np.log(1 + np.abs(fft_result))
            image_result = norm(spec_mag)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "7_fft_spectrum")

            # Spatial example
            A, B = height, width
            kernel = np.array([ [-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
            filtered_x = convolve2d(image_array[:, :, 0], kernel, convolve_type="sobel")
            save_image(filtered_x, "7_spatial")

            plt.imshow(filtered_x, cmap='gray')
            plt.show()

        case "8":
            image_path = 'Figures/butterworth_filters.png' 
            image_array = cv2.imread(image_path)
            height, width,_ = image_array.shape
            plt.imshow(image_array, cmap='gray')
            plt.show()
            save_image(image_array, "8_orig")

            fft_result = np.fft.fft2(image_array[:, :, 0])
            f_shift = np.fft.fftshift(fft_result)

            # Highpass filter
            d0 = 20
            n = 2
            # height = width = 128
            H = highpass_filter(height, width, d0, n)
            filtered_spectrum = f_shift * H
            h_spec_mag = np.log(1 + np.abs(filtered_spectrum))
            image_result = norm(h_spec_mag)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "8_HPF")
            
            # Step 4: Inverse shift
            f_ishift = np.fft.ifftshift(filtered_spectrum)
            
            # Step 5: Inverse FFT
            filtered_image = np.fft.ifft2(f_ishift)
            
            # Take real part (imaginary should be ~0)
            norm_image = np.abs(filtered_image)
            plt.imshow(norm_image, cmap='gray')
            plt.show()
            save_image(norm_image, "8_HPF_result")

            # Low-pass filter
            d0 = 20
            n = 2
            H = lowpass_filter(height, width, d0, n)

            filtered_spectrum = f_shift * H
            h_spec_mag = np.log(1 + np.abs(filtered_spectrum))
            image_result = norm(h_spec_mag)
            plt.imshow(image_result, cmap='gray')
            plt.show()
            save_image(image_result, "8_LPF")
            
            # Step 4: Inverse shift
            f_ishift = np.fft.ifftshift(filtered_spectrum)
            
            # Step 5: Inverse FFT
            filtered_image = np.fft.ifft2(f_ishift)
            
            # Take real part (imaginary should be ~0)
            norm_image = np.abs(filtered_image)
            plt.imshow(norm_image, cmap='gray')
            plt.show()
            save_image(norm_image, "8_LPF_result")

if __name__ == "__main__":
    main()