
# Software guide

1. Load the video file.

2. Load the json file with the same name as the video name.
   
    If the name are different, the json file load fails.
    If do not load the json file, the bboxes and keypoints drawn on the canvas will not be saved.

3. Draw bboxes and keypoints, modify them, and save to the corresponding json file.

    When the current frame is switched, it is automatically saved to the json file.


# Hotkeys

F: Load video

G: Load json

Q: Exit


Z: Pre frame

X: Next frame

Space: Play/Pause


Right click + D: Del bbox
