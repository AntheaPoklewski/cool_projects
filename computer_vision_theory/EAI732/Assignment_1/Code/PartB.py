import scipy
from scipy.io import loadmat
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.gridspec as gridspec
from scipy.stats import norm
import os
import idx2numpy
import matplotlib.pyplot as plt
import numpy as np
import csv
from mlxtend.data import loadlocal_mnist
import csv
import cv2

# ==========================================
# --- 1. SET PATHS & LOAD DATA ---
# ==========================================

def load_data():
    parent = os.path.dirname(os.getcwd())
    dataset_path = "/EAI-Coursework"
    image_file_train = '/Database/train-images-idx3-ubyte/train-images-idx3-ubyte'
    label_file_train = '/Database/train-labels-idx1-ubyte/train-labels-idx1-ubyte'
    image_file_test = '/Database/t10k-images-idx3-ubyte/t10k-images-idx3-ubyte'
    label_file_test = '/Database/t10k-labels-idx1-ubyte/t10k-labels-idx1-ubyte'

    x_train = idx2numpy.convert_from_file(parent + dataset_path + image_file_train)
    label_train = idx2numpy.convert_from_file(parent + dataset_path + label_file_train)
    x_test = idx2numpy.convert_from_file(parent + dataset_path + image_file_test)
    label_test = idx2numpy.convert_from_file(parent + dataset_path + label_file_test)

    x_train_bin = (x_train.reshape(x_train.shape[0], -1) > 127).astype(int)
    x_test_bin = (x_test.reshape(x_test.shape[0], -1) > 127).astype(int)

    df = pd.DataFrame()
    df["train_label"] = label_train
    x_train_df = pd.DataFrame(x_train_bin)
    df = pd.concat([df, x_train_df], axis=1)
    # df.to_csv('my_data.csv', index=False)

    fig, axes = plt.subplots(2, 5, figsize=(10, 5))
    for j, ax in enumerate(axes.flatten()):
        ax.imshow(x_train[j], cmap='gray')  # show the image in grayscale
        ax.set_title(f'Label: {label_train[j]}')   # display the correct digit
        ax.axis('off')                # hide axis for clarity
    plt.tight_layout()
    plt.savefig(f"EAI732/Assignment_1/Figures/Training_data.pdf", dpi=150)
    plt.show()

    return x_train, x_train_bin, label_train, x_test_bin, label_test

class GaussianNaiveBayes:
    def fit(self, X, Y):
        self.classes = np.unique(Y)
        n_samples, n_features = X.shape

        self.priors = np.zeros(len(self.classes)) # P(class) -> P(=5)
        self.means = np.zeros((len(self.classes), n_features))  # mu per pixel per class
        self.variances = np.zeros((len(self.classes), n_features)) # sigma^2 per pixel per class
        
        for i, c in enumerate(self.classes):
            X_c = X[Y == c]
            self.priors[i] = X_c.shape[0]/n_samples # np array (no images of 5/total no images)
            self.means[i] = X_c.mean(axis = 0) # np array 
            self.variances[i] = X_c.var(axis = 0) + 1e-9  # variance + smoothing
                    
    def log_likelihood(self, X):
        """
        Compute log P(pixels | class) for every sample and class.
        Gaussian log-pdf: -0.5 * log(2π σ²) - (x - μ)² / (2σ²)
        Returns shape: (n_samples, n_classes)
        """
        log_likelihoods = np.zeros((X.shape[0], len(self.classes)))
        for i in range(len(self.classes)):
            mu = self.means[i]
            var = self.variances[i]
            # Log Gaussian PDF, summed across all 784 pixels (independence assumption)
            log_p = -0.5 * np.sum(np.log(2 * np.pi * var))           # normalizer
            log_p += -0.5 * np.sum(((X - mu) ** 2) / var, axis=1)    # exponent

            log_likelihoods[:, i] = log_p
        return log_likelihoods
    
    def predict(self, X):
        log_priors = np.log(self.priors)
        log_post = self.log_likelihood(X) + log_priors
        return self.classes[np.argmax(log_post, axis = 1)]

    def score(self, X, Y):
        return np.mean(self.predict(X) == Y)*100

def gaussian_naive_bayes(X_train, Y_train):
    # ── Train ──────────────────────────────────────────────────────────────────────
    classes = np.unique(Y_train)
    priors  = np.zeros(10)
    means   = np.zeros((10, 784))
    variances = np.zeros((10, 784))

    for i, c in enumerate(classes):
        X_c = X_train[Y_train == c]
        priors[i] = X_c.shape[0]/len(X_train)
        means[i] = X_c.mean(axis=0)
        variances[i] = X_c.var(axis=0) + 1e-9

    return priors, means, variances

def predict_gaussian(X, priors, means, variances):
    scores = np.zeros((len(X), 10))
    for i in range(10):
        scores[:, i] = (
            np.log(priors[i])
            - 0.5 * np.sum(np.log(2 * np.pi * variances[i]))
            - 0.5 * np.sum(((X - means[i]) ** 2) / variances[i], axis=1)
        )
    return np.argmax(scores, axis=1)

def bernoulli(X_train, Y_train):
    probs = np.zeros((10, 784))
    priors = np.zeros(10)

    for i, c in enumerate(range(10)):
        X_c = X_train[Y_train == c]
        priors[i] = X_c.shape[0] / len(X_train)
        probs[i]  = (X_c.sum(axis=0) + 1) / (X_c.shape[0] + 2)   # Laplace smoothing
    return probs, priors

def predict_bernoulli(X, probs, priors):
    scores = np.zeros((len(X), 10))
    for i in range(10):
        scores[:, i] = (
            np.log(priors[i])
            + X @ np.log(probs[i])              # pixel ON contribution
            + (1 - X) @ np.log(1 - probs[i])   # pixel OFF contribution
        )
    return np.argmax(scores, axis=1)

def hog_features(image, cell_size=7, n_bins=9):
    image = image.reshape(28, 28)

    # Step 1 — gradients
    gx = np.zeros_like(image)
    gy = np.zeros_like(image)
    gx[:, 1:-1] = image[:, 2:] - image[:, :-2]
    gy[1:-1, :] = image[2:, :] - image[:-2, :]
    magnitude = np.sqrt(gx**2 + gy**2)
    angle     = np.arctan2(gy, gx) * 180 / np.pi % 180

    # Step 2+3 — cell histograms
    n_cells = 28 // cell_size
    bin_width = 180 / n_bins
    features = []

    for r in range(n_cells):
        for c in range(n_cells):
            # extract cell
            m = magnitude[r*cell_size:(r+1)*cell_size,
                          c*cell_size:(c+1)*cell_size]
            a = angle    [r*cell_size:(r+1)*cell_size,
                          c*cell_size:(c+1)*cell_size]

            # build histogram
            hist = np.zeros(n_bins)
            for mag, ang in zip(m.flat, a.flat):
                hist[int(ang / bin_width) % n_bins] += mag
            features.extend(hist)

    return np.array(features)   # shape (144,) for 4x4 grid, 9 bins

def plot_hog_gradients(image, cell_size=7, n_bins=9):
    image = image.reshape(28, 28)

    # Compute gradients
    gx = np.zeros_like(image)
    gy = np.zeros_like(image)
    gx[:, 1:-1] = image[:, 2:] - image[:, :-2]
    gy[1:-1, :] = image[2:, :] - image[:-2, :]
    magnitude = np.sqrt(gx**2 + gy**2)
    angle     = np.arctan2(gy, gx) * 180 / np.pi % 180

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].imshow(image,     cmap='gray')
    axes[0].set_title('Original')

    axes[1].imshow(gx,        cmap='RdBu')
    axes[1].set_title('Gradient X')

    axes[2].imshow(gy,        cmap='RdBu')
    axes[2].set_title('Gradient Y')

    axes[3].imshow(magnitude, cmap='hot')
    axes[3].set_title('Gradient Magnitude')

    for ax in axes:
        ax.axis('off')

    plt.suptitle('HOG Gradient Decomposition')
    plt.savefig(f"EAI732/Assignment_1/Figures/HOG.pdf", dpi=150)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Show data
    x_raw, X_train, Y_train, X_test, Y_test = load_data()

    # HOG 
    X_hog_train = np.array([hog_features(img) for img in X_train])
    print(f"Feature shape: {X_hog_train.shape}")   # (60000, 144)
    plot_hog_gradients(X_test[0])

    # ── Gaussian ───────────────────────────────────────────────────────────────────
    # Train data
    priors, means, variances = gaussian_naive_bayes(X_train, Y_train)
    # Test data
    y_pred = predict_gaussian(X_test, priors, means, variances)
    print(f"Accuracy: {np.mean(y_pred == Y_test):.2%}")

    # Confusion Matrix for testing 
    cm = np.zeros((10, 10), dtype=int)

    for true, pred in zip(Y_test, y_pred):
        cm[true][pred] += 1

    plt.figure(figsize=(10, 8))
    plt.imshow(cm, cmap='Blues')
    plt.colorbar()
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix Gaussian')
    for i in range(10):
        for j in range(10):
            plt.text(j, i, str(cm[i][j]), ha='center', va='center',
                    color='white' if cm[i][j] > cm.max()/2 else 'black')
    plt.tight_layout()
    plt.savefig(f"EAI732/Assignment_1/Figures/Gaussian_NB.pdf", dpi=150)
    plt.show()

    # Class Implementation
    # model = GaussianNaiveBayes()
    # model.fit(x_train_bin, label_train) # <- used to create gaussian info

    # accuracy = model.score(x_test_bin, label_test) # gaussian info used to predict y label_test based on x_test
    # print(f"Accuracy: {accuracy:.4f}")   

    # ── Bernoulli ───────────────────────────────────────────────────────────────────
    X_bin_train = (X_train > 0.5).astype(float)
    X_bin_test = (X_test > 0.5).astype(float)

    # Train data
    probs, priors = bernoulli(X_bin_train, Y_train)
    # Test data
    y_pred = predict_bernoulli(X_bin_test, probs, priors)
    print(f"Accuracy: {np.mean(y_pred == Y_test):.2%}")   # ~84%

    # Confusion Matrix for testing 
    cm = np.zeros((10, 10), dtype=int)

    for true, pred in zip(Y_test, y_pred):
        cm[true][pred] += 1

    plt.figure(figsize=(10, 8))
    plt.imshow(cm, cmap='Blues')
    plt.colorbar()
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix Bernoulli')
    for i in range(10):
        for j in range(10):
            plt.text(j, i, str(cm[i][j]), ha='center', va='center',
                    color='white' if cm[i][j] > cm.max()/2 else 'black')
    plt.tight_layout()
    plt.savefig(f"EAI732/Assignment_1/Figures/Bernoulli_NB.pdf", dpi=150)
    plt.show()