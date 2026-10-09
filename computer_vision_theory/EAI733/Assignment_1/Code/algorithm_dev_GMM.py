import numpy as np
import cv2
from sklearn.mixture import GaussianMixture
from skimage import color, filters, io
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
from skimage.transform import resize

class BlobworldSegmentation:
    def __init__(self, k_range=(2, 5)):
        self.k_range = k_range
        self.best_k = None
        self.labels = None
        self.features = None
        
    def extract_color_features(self, image, scale = 2.0):
        lab_image = color.rgb2lab(image / 255.0)
        lab_smooth = np.zeros_like(lab_image)
        for i in range(3):
            lab_smooth[:, :, i] = gaussian_filter(lab_image[:, :, i], sigma=scale)
        return lab_smooth

    def extract_texture_features(self, image):
        lab = color.rgb2lab(image/255.0)
        L_channel = lab[:, :, 0]
        dy, dx = np.gradient(L_channel)

        Ixx = gaussian_filter(dx * dx, sigma=2.0)
        Ixy = gaussian_filter(dx * dy, sigma=2.0)
        Iyy = gaussian_filter(dy * dy, sigma=2.0)

        trace = Ixx + Iyy
        det = Ixx * Iyy - Ixy * Ixy

        discriminant = np.maximum(trace**2 - 4*det, 0)  # Ensure non-negative
        lambda1 = (trace + np.sqrt(discriminant)) / 2
        lambda2 = (trace - np.sqrt(discriminant)) / 2
        
        # Avoid division by zero
        eps = 1e-10
        lambda1 = np.maximum(lambda1, eps)
        
        # Texture descriptors
        anisotropy = (lambda1 - lambda2) / lambda1  # 0 to 1
        contrast = 2 * np.sqrt(lambda1 + lambda2)   # Normalized
        
        # Normalize contrast to [0, 1]
        contrast = contrast / (contrast.max() + eps)
        
        # Polarity (simplified - would need full implementation)
        # For simplicity, using a placeholder
        polarity = np.ones_like(anisotropy) * 0.5

        # Modulate by contrast (meaningless in low-contrast regions)
        texture = np.stack([
            anisotropy * contrast,
            polarity * contrast,
            contrast
        ], axis=2)
        
        return texture

    def create_feature_vectors(self, image):
        height, width = image.shape[:2]
        color_features = self.extract_color_features(image)
        texture_features = self.extract_texture_features(image)

        # Create position features (normalized to [0, 1])
        y_coords, x_coords = np.meshgrid(
            np.arange(height) / height,
            np.arange(width) / width,
            indexing='ij'
        )
        position_features = np.stack([y_coords, x_coords], axis=2)
        
        # Concatenate all features
        all_features = np.concatenate([
            color_features,      # L, a, b (3D)
            texture_features,    # anisotropy*c, polarity*c, contrast (3D)
            position_features    # x, y (2D)
        ], axis=2)
        
        # Reshape to (N, 8)
        features = all_features.reshape(-1, 8)
        
        self.height = height
        self.width = width
        
        return features

    def compute_mdl_score(self, gmm, features):
        N = features.shape[0]  # Number of samples
        d = features.shape[1]  # Dimensionality
        K = gmm.n_components  # Number of clusters
        
        # Log likelihood
        log_likelihood = gmm.score(features) * N
        
        # Number of free parameters
        # K-1 (mixing weights) + K*d (means) + K*d*(d+1)/2 (covariances)
        m_k = (K - 1) + K * d + K * d * (d + 1) // 2
        
        # MDL score
        mdl_score = log_likelihood - (m_k / 2) * np.log(N)
        
        return mdl_score

    def fit_em(self, features, K, n_init=4):
        gmm = GaussianMixture(
            n_components=K,
            covariance_type='full',  # Full covariance matrices
            n_init=n_init,
            max_iter=10,
            tol=1e-2,
            random_state=42
        )
        
        gmm.fit(features)
        
        return gmm

    def segment(self, image):
        features = self.create_feature_vectors(image)
        self.features = features

        best_score = -np.inf
        best_gmm = None
        best_k = None

        for K in range(self.k_range[0], self.k_range[1] + 1):
            # print(f"  Trying K={K}...")
            gmm = self.fit_em(features, K)
            mdl_score = self.compute_mdl_score(gmm, features)
            
            # print(f"    MDL score: {mdl_score:.2f}")
            
            if mdl_score > best_score:
                best_score = mdl_score
                best_gmm = gmm
                best_k = K
        
        self.best_k = best_k
        
        # Step 3: Get cluster assignments
        labels_1d = best_gmm.predict(features)
        
        # Step 4: Reshape to image dimensions
        labels = labels_1d.reshape(self.height, self.width)
        
        # Step 5: Post-processing (simplified)
        # In the paper, they do boundary refinement and spatial smoothing
        # For simplicity, we'll just apply median filter
        
        labels = median_filter(labels, size=3)
        
        self.labels = labels
        
        return labels, best_k

    def create_segmented_image(self, image, labels):
        segmented = np.zeros_like(image)
        
        for label in np.unique(labels):
            mask = labels == label
            mean_color = image[mask].mean(axis=0)
            segmented[mask] = mean_color
        
        return segmented

def save_image(image_info, q):
    # Create figure and axis
    fig, ax = plt.subplots()

    ax.imshow(image_info)

    # Add labels
    ax.set_xlabel("X Pixel Coordinate")
    ax.set_ylabel("Y Pixel Coordinate")

    # Save
    save_path = "/Users/anthea/Documents/GitHub/EAI733/Assignment_1/Results/"
    fig.savefig(f"{save_path}GMM_{q}.pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    image_path = 'Figures/mean_shift_clustering.png' 
    image = cv2.imread(image_path)
    if image.shape[0] > 200:
        scale = 200 / image.shape[0]
        new_shape = (int(image.shape[0] * scale), int(image.shape[1] * scale))
        image = (resize(image, new_shape) * 255).astype(np.uint8)

    segmenter = BlobworldSegmentation(k_range=(2, 5))
    labels, n_segments = segmenter.segment(image)
    
    # Create visualization
    segmented = segmenter.create_segmented_image(image, labels)

    save_image(segmented, "final")

    # Plot results
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(image)
    axes[0].set_title('Original Image')
    axes[0].axis('off')
    
    axes[1].imshow(labels, cmap='tab10')
    axes[1].set_title(f'Segmentation Labels\n(K={n_segments})')
    axes[1].axis('off')
    
    axes[2].imshow(segmented.astype(np.uint8))
    axes[2].set_title('Segmented Image\n(Mean Colors)')
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()