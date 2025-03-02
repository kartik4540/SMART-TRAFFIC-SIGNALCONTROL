import torch
import cv2
import numpy as np
from PIL import Image
import time

# Load YOLOv5 model
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True, force_reload=False)

def count_cars(image_path, confidence_threshold=0.4):
    """Detect cars in an image and return the count."""
    img = Image.open(image_path)
    results = yolo_model(img)

    # Extract detection results
    detected_objects = results.pandas().xyxy[0]
    car_classes = ['car', 'truck', 'bus', 'motorcycle']

    # Filter by class and confidence threshold
    cars = detected_objects[(detected_objects['name'].isin(car_classes)) & 
                            (detected_objects['confidence'] >= confidence_threshold)]

    return len(cars), results

def calculate_timer(car_count):
    """Calculate red light timer based on car count."""
    return min(max(10, car_count * 5), 30)

def draw_traffic_ui(active, next_adjacent, timers, green_remaining, red_remaining):
    """Display traffic light status using OpenCV."""
    # Create a blank image
    img = np.zeros((500, 500, 3), dtype=np.uint8)

    # Define positions for signals
    positions = {
        'North': (200, 50),
        'East': (400, 200),
        'South': (200, 400),
        'West': (50, 200),
    }

    # Draw traffic signals
    for direction, pos in positions.items():
        if direction == active:
            color = (0, 255, 0)  # Green
            text = f"{green_remaining} sec"
        elif direction == next_adjacent:
            color = (0, 255, 255)  # Yellow (Still RED but showing wait time)
            text = f"Wait: {red_remaining} sec"
        else:
            color = (0, 0, 255)  # Red
            text = "RED"

        cv2.circle(img, pos, 40, color, -1)
        cv2.putText(img, text, (pos[0] - 30, pos[1] + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Display the UI
    cv2.imshow("Traffic Light Simulation", img)

    # Wait for ESC key to exit
    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()

def process_intersection(images, max_cycles=5):
    """Process all four directions at an intersection."""
    timers = {}

    # Count cars and calculate timers for each direction
    for direction, image_path in images.items():
        car_count, _ = count_cars(image_path)
        timers[direction] = calculate_timer(car_count)

    # Define circular order of traffic signals
    order = ['North', 'East', 'South', 'West']

    for cycle in range(max_cycles):
        for i in range(4):
            active = order[i]  # Current GREEN signal
            next_adjacent = order[(i + 1) % 4]  # Next direction (waiting)
            red_1 = order[(i + 2) % 4]  # Completely RED
            red_2 = order[(i + 3) % 4]  # Completely RED

            # Get the green duration for active light
            green_time = timers[active]

            # Countdown Timer for GREEN Light and Next RED Light
            for remaining_time in range(green_time, 0, -1):
                draw_traffic_ui(active, next_adjacent, timers, remaining_time, remaining_time)
                print(f"\n{active} is GREEN for {remaining_time} seconds")
                print(f"{next_adjacent} is waiting for {remaining_time} seconds")
                print(f"{red_1} & {red_2} are RED")

                time.sleep(1)

            print("\nSwitching signals...\n")

# Example Usage: Replace these with actual image paths
images = {
    'North': r'C:\Users\91989\Desktop\as.jpg',
    'East': r"C:\Users\91989\Desktop\download.jpg",
    'South': r"C:\Users\91989\Desktop\download (1).jpg",
    'West': r"C:\Users\91989\Desktop\asdas.jpg"
}

process_intersection(images)
