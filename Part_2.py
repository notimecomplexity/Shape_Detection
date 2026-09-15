import cv2
import numpy as np

COLOR_RANGES = {
    "red": [((0, 180, 100), (8, 255, 255)),
            ((172, 180, 100), (179, 255, 255))],
    "yellow": [((25, 180, 180), (35, 255, 255))],
    "blue": [((95, 180, 100), (112, 255, 255))],
    "purple": [((140, 75, 130), (165, 190, 255))],
    "green": [((48, 160, 140), (56, 215, 190))],
}

def detect_shapes(frame):
    """Detect visible colored regions using only the current frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w = frame.shape[:2]
    # Scale pixel thresholds relative to the original 1920 x 1080 video.
    scale = (h * w) / (1920 * 1080)
    kernel_size = max(3, int(round(5 * np.sqrt(scale))) | 1)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    detections = []
    combined_mask = np.zeros((h, w), dtype=np.uint8)

    for color, ranges in COLOR_RANGES.items():
        mask = np.zeros((h, w), dtype=np.uint8)
        for lower, upper in ranges:
            mask |= cv2.inRange(hsv, np.array(lower, dtype=np.uint8),
                               np.array(upper, dtype=np.uint8))

        # Remove small grass patches, then close compression holes.
        # Replicate the border so clipped foreground is not eroded away there.
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel,
                               borderType=cv2.BORDER_REPLICATE)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel,
                               borderType=cv2.BORDER_REPLICATE)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        pieces = []
        total_area = total_m10 = total_m01 = 0.0
        any_border = False
        for contour in contours:
            x, y, cw, ch = cv2.boundingRect(contour)
            touches_border = (x <= 1 or y <= 1 or
                              x + cw >= w - 1 or y + ch >= h - 1)
            area = cv2.contourArea(contour)
            min_area = (200 if touches_border else 3000) * scale
            if area < min_area:
                continue

            # Occlusion can make a visible shape concave: do not reject it
            # by solidity or replace its boundary with a convex hull.
            moments = cv2.moments(contour)
            if moments["m00"] == 0:
                continue
            pieces.append(contour)
            total_area += moments["m00"]
            total_m10 += moments["m10"]
            total_m01 += moments["m01"]
            any_border |= touches_border
            cv2.drawContours(combined_mask, [contour], -1, 255, -1)

        # This video has one object per color. An occluding object can split
        # it into several visible pieces, which still share one centroid.
        if pieces:
            center = (int(total_m10 / total_area),
                      int(total_m01 / total_area))
            detections.append({"color": color, "contours": pieces,
                               "center": center, "area": total_area,
                               "touches_border": any_border})

    return detections, combined_mask


def annotate_frame(frame, detections):
    finished = frame.copy()
    for detection in detections:
        cx, cy = detection["center"]
        cv2.drawContours(finished, detection["contours"], -1,
                         (255, 255, 255), 2)
        cv2.circle(finished, (cx, cy), 5, (0, 0, 0), -1)
        label = f"{detection['color']}: {cx}, {cy}"
        if detection["touches_border"]:
            label += " TOUCHING"
        (text_width, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
                                            0.6, 2)
        text_x = max(0, min(cx, frame.shape[1] - text_width - 1))
        cv2.putText(finished, label, (text_x, max(20, cy - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return finished


def main():
    cap = cv2.VideoCapture("Assets/Part_2.mp4")
    if not cap.isOpened():
        raise RuntimeError("Could not open video source.")

    out = None
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not np.isfinite(fps) or fps <= 0:
            fps = 30.0
        out = cv2.VideoWriter("analyzed_output.mp4",
                              cv2.VideoWriter_fourcc(*"mp4v"), fps,
                              (width, height))
        if not out.isOpened():
            raise RuntimeError("Could not open output video writer.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            detections, mask = detect_shapes(frame)
            finished = annotate_frame(frame, detections)
            out.write(finished)
            # cv2.imshow("Test", mask)
            cv2.imshow("Video Analysis Stream", finished)
            # Uncomment to inspect the accepted foreground regions.
            # cv2.imshow("Shape masks", mask)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
