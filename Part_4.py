# frame → smooth → edges → connect gaps → candidate contours
#       → score candidates → accepted regions → contours and centroids

import cv2
import numpy as np

# -----------------------------------------------------------------------

# distance between pinhole (camera) and film (2D surface)
FX = 2564.3186869
FY = 2569.70273111 # ideally, FX = FY
# principle point offset
CX = 0.0
CY = 0.0 # optical axis passes through origin of image coordinate system

# CIRCLE_RADIUS_IN = 10.0 # radius of orange circle, measured in inches

validated_depths = [
    238.37928273271842,
    237.5718195970535,
    240.1370862647439,
    238.71230515910716,
    239.1319886681717,
    237.80185417421677,
    239.02892051032845,
    238.57758724594535,
    240.81374284973654,
    238.6035068058387,
    240.29234429957722,
    238.86542047691793,
    239.5765359447182,
    240.53932139672992,
    239.1058352255696,
    240.0079119609715,
    239.37493309803256,
    237.45438835488397,
    240.41126011540243,
    238.580784589488,
    239.67828428488417,
    240.34665393442853,
    237.49768222153804,
    239.4580693347821,
    240.6577761025125,
    236.3498340528356,
    240.61946556809912,
    240.4721027239736,
    236.1354582073889,
    240.74404526304065
]

# print("Median after first 10:", float(np.median(validated_depths[0:9])))
# print("Median after first 20:", float(np.median(validated_depths[0:19])))
# print("Median after first 30:", float(np.median(validated_depths)))

FIXED_Z_IN = float(np.median(validated_depths))

# -----------------------------------------------------------------------


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

    # -----------------------------------------------------------------------

    # circle_contour = None
    # best_circularity = 0.0

    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     if area < 1044:
    #         continue
            
    #     perimeter = cv2.arcLength(contour, True)
    #     if perimeter == 0:
    #         continue

    #     circularity = 4 * np.pi * area / perimeter**2
        
    #     if circularity > best_circularity:
    #         best_circularity = circularity
    #         circle_contour = contour

    # print(f"Best circularity: {best_circularity:.3f}") # statistics

    # circle_fit = None
    # depth_in = None

    # if circle_contour is not None and best_circularity > 0.80:
    #     h, w = frame.shape[:2]
    #     x, y, cw, ch = cv2.boundingRect(circle_contour)

    #     touches_border = (
    #         x <= 1 or y <= 1 or
    #         x + cw >= w - 1 or
    #         y + ch >= h - 1
    #     )

    #     if not touches_border:
    #         (center_u, center_v), radius_px = cv2.minEnclosingCircle(
    #             circle_contour
    #         )

    #         if radius_px > 0:
    #             focal_px = (FX + FY) / 2
    #             depth_in = focal_px * CIRCLE_RADIUS_IN / radius_px
    #             circle_fit = (center_u, center_v, radius_px)

    # -----------------------------------------------------------------------

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

        # -----------------------------------------------------------------------

        # if depth_in is not None:
        #     X = (cx - CX) * depth_in / FX
        #     Y = (cy - CY) * depth_in / FY
        #     Z = depth_in

        #     label = f"X:{X:.1f} Y:{Y:.1f} Z:{Z:.1f} in"
        # else:
        #     label = f"({cx}, {cy}) Depth unavailable"
        
        # -----------------------------------------------------------------------

        X = (cx - CX) * FIXED_Z_IN / FX
        Y = (cy - CY) * FIXED_Z_IN / FY

        label = f"X:{X:.2f} Y:{Y:.2f} Z:{FIXED_Z_IN:.2f}"

        position = (cx + 8, cy - 8)

        cv2.putText(final_overlay, label, position,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 3, cv2.LINE_AA)

        cv2.putText(final_overlay, label, position,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1, cv2.LINE_AA)

    # -----------------------------------------------------------------------

    # if depth_in is not None:
    #     print(depth_in) # debugging: finding validated_depths members

    # if circle_contour is not None: # magenta outline for shape with best circularity
    #     cv2.drawContours(
    #         final_overlay,
    #         [circle_contour],
    #         -1,
    #         (255, 0, 255),
    #         3,
    #     )
    
    # if circle_fit is not None:
    #     center_u, center_v, radius_px = circle_fit
    #     center = (round(center_u), round(center_v))

    #     # Magenta fitted circle and a line showing its radius.
    #     cv2.circle(
    #         final_overlay, center, round(radius_px),
    #         (255, 0, 255), 1, cv2.LINE_AA
    #     )
    #     cv2.line(
    #         final_overlay,
    #         center,
    #         (round(center_u + radius_px), round(center_v)),
    #         (255, 0, 255), 1
    #     )

    #     debug_text = f"Radius: {radius_px:.1f}px  Depth: {depth_in:.1f}in"

    #     cv2.putText(
    #         final_overlay, debug_text, (20, 30),
    #         cv2.FONT_HERSHEY_SIMPLEX, 0.7,
    #         (0, 0, 0), 3, cv2.LINE_AA
    #     )
    #     cv2.putText(
    #         final_overlay, debug_text, (20, 30),
    #         cv2.FONT_HERSHEY_SIMPLEX, 0.7,
    #         (255, 255, 255), 1, cv2.LINE_AA
    #     )

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
            # cv2.imshow("detect_gray()", g_ou) # debugging for detect_gray
            c_ou, c_ov = detect_colour(frame)
            # cv2.imshow("detect_colour", c_ou) # debugging for detect_colour
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
