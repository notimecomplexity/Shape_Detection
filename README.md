# Penn Aerial Robotics (PennAiR) Software Challenge

## Algorithm (Part 4):
To sketch our outlines, we combine two different edge detection functions with `cv2.bitwise_or()`.

1. Detect smooth regions with `detect_gray()`
<img width="1487" height="887" alt="detect_gray()" src="https://github.com/user-attachments/assets/882fe0f7-5c17-45b4-aa62-76d815ae7d2a" />
- This function converts a frame into **Grayscale**, applies a **Median Blur**, averages **Difference in Texture** over a 9x9 neighborhood (small = dark, large = light) between non-blurred and blurred, selects smooth (dark) regions, and cleans their boundaries. 

## Task Overview:

### Part 1: Shape Detection on Static Image
<img width="960" height="540" alt="Part_1" src="https://github.com/user-attachments/assets/695e3ef8-e2a3-49e9-a738-47a3235e8577" />

### Part 2: Shape Detection on Video
https://github.com/user-attachments/assets/e1292e93-dd82-431b-986f-c9e9a1644195

### Part 3: Background Agnostic Algorithm
https://github.com/user-attachments/assets/2f1050c2-9ce6-41c6-8190-407471c2a60e

### Part 4: Make it 3D
https://github.com/user-attachments/assets/5ae24443-24a6-4b41-8521-698efc411494
