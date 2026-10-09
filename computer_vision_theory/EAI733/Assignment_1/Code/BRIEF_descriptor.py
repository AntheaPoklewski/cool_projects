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