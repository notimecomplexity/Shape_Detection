"""ROS-independent Part 4 detection; pixel geometry assumes original video resolution."""
import cv2
import numpy as np

def detect_gray(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray_blur = cv2.medianBlur(gray, 11)

    gray_float = gray.astype(np.float32)
    gray_blur_float = gray_blur.astype(np.float32)

    gray_detail = np.abs(gray_float - gray_blur_float)

    gray_texture = cv2.boxFilter(gray_detail, -1, (9, 9))

    gray_mask = (gray_texture < 3).astype(np.uint8) * 255

    gray_mask = cv2.GaussianBlur(gray_mask, (11, 11), 3)
    _, gray_mask = cv2.threshold(
        gray_mask, 200, 255, cv2.THRESH_BINARY
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    gray_mask = cv2.dilate(gray_mask, kernel, iterations=1)

    contours, _ = cv2.findContours(
        gray_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    gray_outline = np.zeros_like(gray_mask)
    gray_overlay = frame.copy()

    for contour in contours:
        if cv2.contourArea(contour) < 1044:
            continue

        cv2.drawContours(gray_outline, [contour], -1, 255, 2)
        cv2.drawContours(gray_overlay, [contour], -1, (0, 255, 0), 2)

    return gray_outline, gray_overlay

def detect_colour(frame):
    colour = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    _, a, b = cv2.split(colour)

    a = cv2.GaussianBlur(a, (5, 5), 2)
    b = cv2.GaussianBlur(b, (5, 5), 2)

    colour_outline = cv2.bitwise_or(
        cv2.Canny(a, 15, 60),
        cv2.Canny(b, 15, 60)
    )

    kernel = np.ones((3, 3), dtype=np.uint8)
    colour_outline = cv2.dilate(colour_outline, kernel, iterations=1)

    colour_overlay = frame.copy()
    colour_overlay[colour_outline > 0] = (0, 255, 0)

    return colour_outline, colour_overlay


def analyze_frame(frame, fx=2564.3186869, fy=2569.70273111,
                  principal_x=0.0, principal_y=0.0,
                  depth_in=239.25346088310212):
    """Return per-frame detections and annotated BGR image.

    Assumes a fixed plane parallel to the image plane. No object tracking.
    Uses the challenge's zero principal point literally. No image resizing.
    """
    gray_edges = detect_gray(frame)[0]
    color_edges = detect_colour(frame)[0]
    edges = cv2.bitwise_or(gray_edges, color_edges)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated = frame.copy()
    detections = []
    depth_m = depth_in * 0.0254
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 1044:
            continue
        moments = cv2.moments(contour)
        if moments['m00'] == 0:
            continue
        u = moments['m10'] / moments['m00']
        v = moments['m01'] / moments['m00']
        center = ((u-principal_x)*depth_m/fx,
                  (v-principal_y)*depth_m/fy, depth_m)
        detections.append(dict(center=center, centroid_px=(u,v),
                               outline_px=contour.reshape(-1,2), area_px2=area))
        cv2.drawContours(annotated, [contour], -1, (0,255,0), 2)
        cv2.circle(annotated, (round(u),round(v)), 5, (0,0,255), -1)
        label = f'X:{center[0]:.2f} Y:{center[1]:.2f} Z:{center[2]:.2f} m'
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        pos = (max(0,min(round(u)+8,frame.shape[1]-tw-1)),
               max(20,min(round(v)-8,frame.shape[0]-5)))
        for color, thickness in [((0,0,0),3), ((255,255,255),1)]:
            cv2.putText(annotated,label,pos,cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,color,thickness,cv2.LINE_AA)
    return detections, annotated
