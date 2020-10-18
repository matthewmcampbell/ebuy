import cv2
import pytesseract

img = cv2.imread('/home/matteo/Desktop/s-l1600.jpg')
text = pytesseract.image_to_string(img)
print(text)
