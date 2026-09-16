# Penn Aerial Robotics (PennAiR) Software Challenge

## Table of Contents
- [Task Overview](#task-overview)
- [The Outline](#the-outline)

## Task Overview:

### Part 1: Shape Detection on Static Image
<img width="960" height="540" alt="Part_1" src="https://github.com/user-attachments/assets/695e3ef8-e2a3-49e9-a738-47a3235e8577" />

### Part 2: Shape Detection on Video
https://github.com/user-attachments/assets/e1292e93-dd82-431b-986f-c9e9a1644195

### Part 3: Background Agnostic Algorithm
https://github.com/user-attachments/assets/2f1050c2-9ce6-41c6-8190-407471c2a60e

### Part 4: Make it 3D
https://github.com/user-attachments/assets/5ae24443-24a6-4b41-8521-698efc411494

## The Outline:
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

Performing `cv2.bitwise_or()` on the results of `detect_gray()` and `detect_colour()` allows us to preserve our rough outline of the trapezoid while also improving the outline sharpness of the other four shapes.
