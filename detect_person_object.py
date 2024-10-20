import numpy as np
import argparse
import sys
import cv2
from ultralytics import YOLO
from math import pow, sqrt
from websockets.sync.client import connect
import json

# WebSocket Server URL
ws_url = "ws://localhost:8080"
ws = connect(ws_url)
print(f"Connected to {ws_url}")

def send_message_to_server(message):
    ws.send(message)
    print(f"Sent: {message}")
    response = ws.recv()
    print(f"Received from Server: {response}")

# COCO dataset class names (YOLOv7 is often trained on COCO)
# You might need to adjust these based on the model you're using.
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", 
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", 
    "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", 
    "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", 
    "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", 
    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", 
    "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", 
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", 
    "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet", 
    "TV", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", 
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", 
    "scissors", "teddy bear", "hair drier", "toothbrush"
]

# Load YOLOv7 model
model = YOLO("yolo11n.pt")
# Capture video
cap = cv2.VideoCapture(0)

frame_no = 0
while cap.isOpened():
    frame_no += 1
    ret, frame = cap.read()
    if not ret:
        break

    # Inference
    results = model.predict(frame)

    # Extract detections
    detections = results[0].boxes.xyxy.cpu().numpy()
    class_ids = results[0].boxes.cls.cpu().numpy()  # Extract class IDs

    pos_dict = dict()
    coordinates = dict()
    F = 550  # Focal length

    for i, detection in enumerate(detections):
        x, y, x2, y2 = detection
        # Convert to int
        x, y, x2, y2 = map(int, (x, y, x2, y2))
        coordinates[i] = (x, y, x2, y2)

        # Mid point of bounding box
        x_mid = round((x+x2)/2, 4)
        y_mid = round((y+y2)/2, 4)
        height = round(y2-y, 4)

        class_id1 = int(class_ids[i])
        class_label = COCO_CLASSES[class_id1]
        # Distance from camera based on triangle similarity
        if class_label == "person":
            distance = (165 * F) / height
        elif class_label == "bottle":
            distance = (20 * F) / height

        # Mid-point of bounding boxes (in cm) based on triangle similarity technique
        x_mid_cm = (x_mid * distance) / F
        y_mid_cm = (y_mid * distance) / F
        pos_dict[i] = (x_mid_cm, y_mid_cm, distance)

    close_objects = set()
    for i in pos_dict.keys():
        for j in pos_dict.keys():
            class_id1 = int(class_ids[i])
            class_id2 = int(class_ids[j])
            if i < j and COCO_CLASSES[class_id1] in ["person", "bottle"] and COCO_CLASSES[class_id2] in ["person", "bottle"] and class_id1 != class_id2:
                dist = sqrt(pow(pos_dict[i][0]-pos_dict[j][0], 2) + pow(pos_dict[i][1]-pos_dict[j][1], 2) + pow(pos_dict[i][2]-pos_dict[j][2], 2))
                if dist < 75:  # 200 cm or 2 meters
                    close_objects.add(i)
                    close_objects.add(j)

    for i in pos_dict.keys():
        if i in close_objects:
            COLOR = (0, 0, 255)
            send_message_to_server("red")
        else:
            COLOR = (0, 255, 0)
            send_message_to_server("green")

        (x, y, x2, y2) = coordinates[i]
        class_id = int(class_ids[i])
        class_label = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else "Unknown"
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x2, y2), COLOR, 2)

        # Display object type and distance
        label = f'{class_label}: {round(pos_dict[i][2] / 30.48, 2)} ft'
        cv2.putText(frame, label, (x, y - 15 if y - 15 > 15 else y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)

    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.imshow('Frame', frame)
    cv2.resizeWindow('Frame', 800, 600)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
ws.close()
print("Connection closed")
