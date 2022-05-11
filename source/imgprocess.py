# -*- coding: utf-8 -*-
"""
imgrocess.py: Methods of image preprocessing for DB upload.
Script reads contour of seed on image which is used to calculate dimensions of
given seed in pixels. Additionaly script returns average color for given seed.

__doc__ using Sphnix Style
"""

# Copyright 2022 University Southern Bohemia

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Vojtech Barnat"
__copyright__ = "<2022> <University Southern Bohemia>"
__credits__ = ["Ondrej Budik", "Ivo Bukovsky"]

__license__ = "MIT (X11)"
__version__ = "1.0.4"
__maintainer__ = ["Vojtech Barnat", "Ondrej Budik"]
__email__ = ["Vojtech.Barnat@fs.cvut.cz", "obudik@prf.jcu.cz"]
__status__ = "Beta"

__python__ = "3.8.0"


# Import libs for entire script
import numpy as np
import cv2 as cv2
from scipy.spatial.distance import pdist, squareform

from config import BORDER_SIZE, L_THRESH, H_THRESH, L_AREA, H_AREA

def rotate_point(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.

    Parameters
    ----------
    origin : list
        Origin location in [X, Y] which should be rotated
    point : list
        Point around which should the origin be rotated in [X, Y]
    angle : numeric
        Angle of rotation in radians

    Returns
    -------
    qx : int
        which is the rotated points x coordinate
    qy : int
        which is the rotated points y coordinate

    Raises
    -----
    #TODO nema to delat nejake checky? :)
    """

    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return int(qx), int(qy)


def rgb_to_hex(r, g, b):
    """
    Converts RGB to hex color.

    Parameters
    ----------
    r : int
        Red color of pixel
    g : int
        Green color of pixel
    b : int
        Blue color of pixel

    Returns
    -------
    string format of hex
    """

    return ('{:X}{:X}{:X}').format(r, g, b)


def hex_to_rgb(hex):
    """
    Converts hex color to RGB.

    Parameters
    ----------
    hex : str
        Hexanumerical value

    Returns
    -------
    tuple of rgb in numeric form
    """
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i:i+2], 16)
        rgb.append(decimal)
    return tuple(rgb)


def edge_detector_gray(src):
    """
    Edge detection using sobel operators input image should be in grayscale,
    output is grayscale edge image.

    Parameters
    ----------
    src : uint8 numpy array
        Single channel input image in opencv format

    Returns
    -------
    edges : uint8 numpy array
        Edges of objects in image
    """
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S
    srcg = cv2.GaussianBlur(src, (3, 3), 0)
    src_grad_x = cv2.Sobel(srcg, ddepth, 1, 0, ksize=3, scale=scale,
                           delta=delta, borderType=cv2.BORDER_DEFAULT)
    src_grad_y = cv2.Sobel(srcg, ddepth, 0, 1, ksize=3, scale=scale,
                           delta=delta, borderType=cv2.BORDER_DEFAULT)
    src_abs_grad_x = cv2.convertScaleAbs(src_grad_x)
    src_abs_grad_y = cv2.convertScaleAbs(src_grad_y)
    edges = cv2.addWeighted(src_abs_grad_x, 0.5, src_abs_grad_y, 0.5, 0)
    return edges


def preproces_seed_image(img_path, downscale=0.05, autoload=True):
    """
    Takes image of seed and finds its contour from which its size and average
    color are determined returns int values of size and area average color of
    seed in hex format found contour image.

    Parameters
    ----------
    img : str or pathlib.Path
        Path to image which should be loaded
    downscale : float, optional
        Modifier of downscaling for better performance. Defaults to 0.05.

    Returns
    -------
    max_x_dist : int
        x size of found seed in pixels
    max_y_dist : int
        y size of found seed in pixels
    area : int 
        area of found seed in pixels squared
    hex_color : str
        average color of found seed in hex format
    """
    # Load img from given img path
    if autoload:
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img = img_path

    w = img.shape[1]
    h = img.shape[0]

    # make border
    bs = int(BORDER_SIZE * w)
    r = int(img[0][0][0])
    g = int(img[0][0][1])
    b = int(img[0][0][2])
    img = cv2.copyMakeBorder(img, top=bs, bottom=bs, left=bs, right=bs, borderType=cv2.BORDER_CONSTANT, value=[r,g,b])

    # Convert image to HSV - (hue, saturation, value)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    #take just H - hue
    img_h = img_hsv[:,:,0]

    # de-noising
    kernel = np.ones((5,5),np.uint8)
    img_h = cv2.erode(img_h, kernel, iterations = 2)
    img_h = cv2.dilate(img_h, kernel, iterations = 2)

    #thresholding
    img_bin = cv2.inRange(img_h, L_THRESH, H_THRESH)

    #edge detection
    img_edge = edge_detector_gray(img_bin)

    #find contours
    contours, hierarchy = cv2.findContours(img_edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #sort contours acording to area
    cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

    #pick largest
    large_contours = []
    for contour in cntsSorted:
        area = cv2.contourArea(contour)
        if (area > L_AREA) & (area < H_AREA):
            large_contours.append(contour)

    picked_contour = large_contours[0]
    area = cv2.contourArea(picked_contour)
    contour = picked_contour[:,0,:]

    #calculate distances between points in contour
    dist = pdist(contour)
    dist = squareform(dist)
    #find furthest apart points
    max_x_dist, [i_1, i_2] = np.nanmax(dist), np.unravel_index(np.argmax(dist), dist.shape)
    point1 = contour[i_1]
    point2 = contour[i_2]
    #calculate vector and its angle
    vector = point2 - point1
    angle = np.arctan(vector[1] / vector[0])
    angle = angle * 360 / 2 / np.pi

    #rotate contour points acording to found angle
    rotated_contour = np.zeros((picked_contour.shape), dtype=int)

    #origin of rotation = center if img
    ox, oy = int(w/2), int(h/2)

    #for each point rotate
    for i, point in enumerate(picked_contour):
        new_x, new_y = rotate_point([ox, oy], point[0], -np.radians(angle))
        rotated_contour[i][0][0] = new_x
        rotated_contour[i][0][1] = new_y

    #rotate furthest apart points
    rotated_point1 = rotate_point([ox, oy], point1, -np.radians(angle))
    rotated_point2 = rotate_point([ox, oy], point2, -np.radians(angle))

    #Find the maximum y distance between points in contour
    max_y_index = np.argmax(rotated_contour[:,0,1])
    min_y_index = np.argmin(rotated_contour[:,0,1])
    max_y_dist_point1 = rotated_contour[max_y_index,0,:]
    max_y_dist_point2 = rotated_contour[min_y_index,0,:]
    max_y_dist = rotated_contour[max_y_index,0,1] - rotated_contour[min_y_index,0,1]

    #bounding box from 4 points"
    p1 = rotated_point1
    p2 = rotated_point2
    p3 = max_y_dist_point1
    p4 = max_y_dist_point2
    #crop
    x, y, w, h = cv2.boundingRect(np.array([[p1[0], p3[1]],[p2[0], p4[1]]]))
    cropped = img[y:y+h, x:x+w]

    # lower number of points in contour for speed
    approx_contour = cv2.approxPolyDP(rotated_contour, epsilon=10, closed=True)

    #downscale for speed
    img = cv2.resize(cropped, (0,0), fx=downscale, fy=downscale)
    approx_contour[:, :, 0] = (approx_contour[:, :, 0] -  x) * downscale
    approx_contour[:, :, 1] = (approx_contour[:, :,  1] - y) * downscale

    #find average color inside of contour
    raw_dist = np.empty((img.shape[0], img.shape[1]), dtype=np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            raw_dist[i,j] = cv2.pointPolygonTest(approx_contour, (j,i), True)

    sum_color = [0, 0, 0]
    avg_color = [0, 0, 0]
    total = [0, 0, 0]
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(img.shape[2]):
                if raw_dist[i,j] > 0:
                    sum_color[k] += img[i,j,k]
                    total[k] += 1

    for i in range(3):
        try:
            avg_color[i] = int(sum_color[i] / total[i])
        except ZeroDivisionError:
            print("ZeroDivisionError: Color processing failed on image:"+str(img_path)+"color set to 0. Assign it manually")
            avg_color[i] = 0

    hex_color = rgb_to_hex(avg_color[0], avg_color[1], avg_color[2])

    return int(max_x_dist), int(max_y_dist), int(area), hex_color


if __name__ == "__main__":

    """
    Example of usage
    For every class display results
    """
    from glob import glob
    import os


    subfolders_src = [ f.path for f in os.scandir("test") if f.is_dir() ]

    foldernames = []
    for subfolder_src in subfolders_src:
        foldernames.append(subfolder_src.split("\\")[1])

    class_num = len(foldernames)
    for i, foldername in enumerate(foldernames):
        print("\n" + foldername)
        filenames = glob(os.path.join("to_be_uploaded", foldername,"*.tif"))

        max_x_dist, max_y_dist, area, hex_color = preproces_seed_image(filenames[0])

        print("size_x = " + str(max_x_dist) + " pix")
        print("size_y = " + str(max_y_dist) + " pix")
        print("area = " + str(area) + " pix^2")
        print("color = #" + hex_color)