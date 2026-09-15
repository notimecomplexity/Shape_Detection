# frame → smooth → edges → connect gaps → candidate contours
#       → score candidates → accepted regions → contours and centroids

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

def find_com(frame, edges):
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    final_overlay = frame.copy()

    for contour in contours:
        if cv2.contourArea(contour) < 1044:
            continue

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        cv2.drawContours(final_overlay, [contour], -1, (0, 255, 0), 2)
        cv2.circle(final_overlay, (cx, cy), 5, (0, 0, 255), -1)
        label = f"COM: ({cx}, {cy})"
        position = (cx + 8, cy - 8)

        cv2.putText(final_overlay, label, position,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 3, cv2.LINE_AA)

        cv2.putText(final_overlay, label, position,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1, cv2.LINE_AA)

    return final_overlay

def main():
    cap = cv2.VideoCapture("Assets/Parts_3_4_5.mp4")
    if not cap.isOpened():
        raise RuntimeError("Could not open video source.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            g_ou, g_ov = detect_gray(frame)
            # cv2.imshow("Detect Gray", g_ov) # debugging for detect_gray
            c_ou, c_ov = detect_colour(frame)
            # cv2.imshow("Detect Colour", c_ov) # debugging for detect_colour
            combined_edges = cv2.bitwise_or(g_ou, c_ou)
            final = find_com(frame, combined_edges)
            cv2.imshow("Video Analysis Stream", final)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
