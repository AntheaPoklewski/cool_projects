import numpy as np
import cv2
import glob

# Calculating Ground Truth Geometry
nx, ny = 11, 7
square_size = 0.03
objp = np.zeros((nx * ny, 3), np.float32)

# Given 3D reference system
objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)
objp *= square_size

objpoints = []  # 3D points
imgpoints_l = []  # left image points
imgpoints_r = []  # right image points

images_l = sorted(glob.glob("leftcamera/*.png"))
images_r = sorted(glob.glob("rightcamera/*.png"))

for image_l_path, image_r_path in zip(images_l, images_r):
    img_l = cv2.imread(image_l_path)
    img_r = cv2.imread(image_r_path)

    gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
    gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

    ret_l, corners_l = cv2.findChessboardCorners(gray_l, (nx, ny), None)
    ret_r, corners_r = cv2.findChessboardCorners(gray_r, (nx, ny), None)

    if ret_l and ret_r:
        objpoints.append(objp)
