# Penn Aerial Robotics (PennAiR) Software Challenge

## Table of Contents
- [Task Overview](#task-overview)
- [The Outline](#the-outline)
- [The COM](#the-com)
- [ROS 2](#ros-2)

## Task Overview

### Part 1: Shape Detection on Static Image
<img width="960" height="540" alt="Part_1" src="https://github.com/user-attachments/assets/695e3ef8-e2a3-49e9-a738-47a3235e8577" />

### Part 2: Shape Detection on Video
https://github.com/user-attachments/assets/e1292e93-dd82-431b-986f-c9e9a1644195

### Part 3: Background Agnostic Algorithm
https://github.com/user-attachments/assets/2f1050c2-9ce6-41c6-8190-407471c2a60e

### Part 4: Make it 3D
https://github.com/user-attachments/assets/5ae24443-24a6-4b41-8521-698efc411494

## The Outline
To sketch our outlines, we combine two different edge detection functions with `cv2.bitwise_or()`.

1. Detect smooth regions with `detect_gray()`
<img width="1487" height="887" alt="Gray Process" src="https://github.com/user-attachments/assets/7acaac9c-0d38-4105-9502-fb728ee23da2" />

- This function converts a frame into **Grayscale**, applies a **Median Blur**, averages texture differences over a 9x9 neighbourhood (small = dark, large = light) between non-blurred and blurred, selects smooth (dark) regions, and cleans their boundaries.

<img width="1624" height="997" alt="Gray Final" src="https://github.com/user-attachments/assets/87d4a9a2-b3eb-4420-b96c-e670b6e3f1fd" />

- Each shape's rough outline is captured, but the accuracy could be improved. To accomplish this, we utilise a second function `detect_colour()`.

2. Detect colour regions with `detect_colour()`
<img width="1512" height="887" alt="Colour Process" src="https://github.com/user-attachments/assets/c0a7b108-cb95-4b02-9747-46ee5a6cc58e" />

- This function converts a frame into **Lab (Lightness, a: Green-Red, b: Blue-Yellow)**, applies a **Gaussian Blur** on **a** and **b**, combines their **Canny Edge Detection** results with `cv2.bitwise_or()`, and thickens the outlines by one pixel in each direction.

<img width="1624" height="998" alt="Colour Final" src="https://github.com/user-attachments/assets/b06a67e6-76a7-4431-8ed4-29635682960f" />

- Sharp outlines are returned for every shape except the trapezoid, as its colour profile **(Black-White)** was completely undetected in **a** and **b**.

Performing `cv2.bitwise_or()` on the results of `detect_gray()` and `detect_colour()` allows us to preserve our rough outline of the trapezoid while also improving the outline sharpness of the other four shapes, returning a binary edge image `edges_combined`.

## The COM
1. `cv2.findContours()` extracts boundaries from `combined_edges`, returning `contours`.
- `contours`: a collection of boundaries, each an array of (x, y) pixel coordinates.
2. For each `contour` in `contours`, we derive its **COM (Center of Mass)** with the formula

   $$(x_c = \frac{\sum_i m_i x_i}{\sum_i m_i}, y_c = \frac{\sum_i m_i y_i}{\sum_i m_i})$$

   where $$\sum_i m_i$$, $$\sum_i m_i x_i$$, and $$\sum_i m_i y_i$$ are calculated with `cv2.moments()`.
3. In **Part 4**, we convert the units of $$x_c$$ and $$y_c$$ from pixels to inches due to transitioning from a 2D to 3D environment.
4. To determine the z-coordinate $$Z$$ of each shape, equivalent to the distance from the camera to screen, we use the formula

   $$Z \approx \frac{fR}{r}$$

   where $$f$$ is the focal length of the camera in pixels $$(f_x \approx f_y \approx 2567.01070901)$$, $$R$$ is the radius of the circle in inches $$(R = 10)$$, and $$r$$ is the radius of the circle in pixels, which we will derive below.
5. For each frame, we detected the `contour` with the best circularity $$(c_{best})$$, changing its outline to magenta.
- Circularity measures how close a shape is to a circle, where $$0 \leq c \leq 1$$.
6. Taking a random sample of 60 frames, we measured which shape had the best circularity.
  
    | Shape | Circle | Pentagon | Rectangle | Trapezoid | Triangle |
    |----------|----------|----------|----------|----------|----------|
    | $$c_{average}$$ | 0.81 | 0.75 | 0.69 | 0.66 | N.A. |
  
    As expected, the **Circle** had the highest $$c_{average}$$, so we set our $$c_{threshold} = 0.80$$.
  7. For each frame, if $$c_{best} > c_{threshold}$$, we assume the contour with $$c_{best}$$ is the **Circle** and proceed with estimating $$r$$. We then draw a magenta circle over the existing outline about its COM $$(x_c, y_c)$$ and output our calculated $$Z$$ in the **Terminal**.
  8. We manually analyse the output video frame-by-frame, selecting frames where the magenta circle overlaps near-perfectly with the **Circle's** boundary, adding the calculated $$Z$$ to an array `validated_depths`.

      | $$n$$ | 10 | 20 | 30 |
      |----------|----------|----------|----------|
      | $$Z_{median}$$ | 238.71230515910716 | 239.1058352255696 | 239.25346088310212 |

     Since $$Z_{median}$$ increased by only 0.06% as our number of measurements $$n$$ increased from 20 to 30, we can conclude that:

     $$Z = 239.25$$ $$\text{inches}$$ $$(\text{2.d.p.})$$

## ROS 2

Requires Ubuntu 24.04 with ROS 2 Jazzy installed. Run these commands inside Ubuntu.

### Install dependencies

```bash
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install ros-dev-tools ros-jazzy-cv-bridge python3-opencv python3-numpy
```

### Build

From the repository's root directory:

```bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Run

While still in `ros2_ws`, run:

```bash
ros2 launch pennair_vision shapes.launch.py \
  video_path:="$(realpath ../Assets/Parts_3_4_5.mp4)" \
  fps:=10.0 show_debug:=false loop:=true
```

This assumes `ros2_ws` and `Assets` are in the same parent directory. If you copied the workspace separately, replace the `video_path` value with the video's absolute path inside Ubuntu.

Options:
- `fps:=10.0`: publishes at 10 frames per second; `0.0` uses the video's FPS.
- `show_debug:=true`: displays annotated frames; requires a graphical desktop.
- `loop:=true`: repeats the video.

Press **Ctrl+C** in the launch terminal to stop.

### Inspect detections

In a second Ubuntu terminal, from the repository root:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 topic list -t
ros2 topic echo /shapes/detections --once
```

Topics:
- `/camera/image_raw`: input video frames.
- `/shapes/detections`: detected centers, outlines, and areas.
- `/shapes/annotated`: annotated output frames.

Centers are in meters in the camera optical frame: $$x_c$$ right, $$y_c$$ down, $$Z$$ forward. Outline points and image centroids are in pixels; their z-coordinate is 0. Detection IDs are local to each frame, not tracking IDs.

Depth is fixed using the **Part 4** calibration, assuming all shapes lie on a stationary plane parallel to the image plane.
