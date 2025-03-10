import cv2
import numpy as np

from PIL import Image

#conversion
def pil2array(pil_image):
    array_image = np.array(pil_image)
    alpha_removed = remove_alpha(array_image)
    bgr_image = rgb2bgr(alpha_removed)
    converted = bgr_image
    return converted

def remove_alpha(array_image):
    if array_image.shape[-1] == 4:
        array_image = array_image[:, :, :3]
    return array_image

def rgb2bgr(array_image):
    return cv2.cvtColor(array_image, cv2.COLOR_RGB2BGR)

#image preprocessing
def thresholded_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 4)
    cv2.imwrite('app/uploads/thresh.png', thresh)
    cv2.imwrite('app/uploads/adaptive.png', adaptive)
    return adaptive

def get_normalized_image(img):
    # Get grayscale image for better processing
    resized_height = 480
    percent = resized_height / len(img)
    resized_width = int(percent * len(img[0]))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    gray = cv2.resize(gray,(resized_width,resized_height))
    try:
        start_point = (0, 0) 
        end_point = (gray.shape[0], gray.shape[1]) 
        color = (255, 255, 255) 
        thickness = 10
        gray = cv2.rectangle(gray, start_point, end_point, color, thickness) 
    except:
        print("Failed to crop border")
    gray = cv2.bitwise_not(gray)
    
    return gray

def get_skew_angle(gray):
    # Gets skew angle to fix text rotation on the image
    thresh = cv2.threshold(gray, 50, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel)
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imwrite('app/uploads/contours.jpg', cv2.drawContours(gray, contours, -1, (255, 255, 0), 3))

    # Determine contours of text and other objects on the image
    angles = []
    for contour in contours:
        minAreaRect = cv2.minAreaRect(contour)
        print(minAreaRect)
        angle = minAreaRect[-1]
        if angle not in [90.0, 0.0] and abs(angle) <= 16:
            angles.append(angle)
    
    # Get angle average of all contours
    angles.sort()
    mid_angle = angles[int(len(angles)/2)]
    return mid_angle

def deskew(image):
    # Fix the skew angle of the image
    original = image
    img = get_normalized_image(image)
    angle = get_skew_angle(img)
    if angle > 45: #anti-clockwise
        angle = -(90 - angle)
    height = original.shape[0]
    width = original.shape[1]
    m = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
    deskewed = cv2.warpAffine(original, m, (width, height), borderValue=(255,255,255))
    cv2.imwrite('app/uploads/deskewed.jpg', deskewed)
    return deskewed

def denoise(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    denoised = cv2.medianBlur(image, 1)
    #denoised = cv2.bilateralFilter(image, 9, 75, 75)
    #denoised = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    cv2.imwrite('app/uploads/denoised_med.png', denoised)
    return denoised