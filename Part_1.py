import cv2 # OpenCV
import numpy as np # Mathematics

# Reads Static Image
img = cv2.imread("Assets/Part_1.png", cv2.IMREAD_COLOR)

# Applies Gaussian Blur to reduce background noise
blur = cv2.GaussianBlur(img, (9, 9), 1.4)
 
# Applies Canny Edge Detector
edges = cv2.Canny(blur, threshold1=100, threshold2=200)
 
# Close small gaps so each object's outline is one contour
closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

out = img.copy()
min_area = 1000 # Filters out background contours

for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area < min_area:
        continue

    M = cv2.moments(cnt)
    if M["m00"] == 0:
        continue

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    print(f"Object {i}: center of mass = ({cx}, {cy}), area = {area:.0f}")

    cv2.drawContours(out, [cnt], -1, (255, 255, 255), 2)
    cv2.circle(out, (cx, cy), 5, (0, 0, 0), -1)
    cv2.putText(out, f"{cx}, {cy}", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

# cv2.imshow("Canny Edge Detection", edges) # for debugging
cv2.imshow("Centers of Mass", out)
cv2.waitKey(0)
cv2.destroyAllWindows()