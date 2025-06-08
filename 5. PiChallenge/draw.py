import pyautogui
import math
import time

# Give yourself 5 seconds to move to Paint window
wait = True
total_wait = 5
while wait:
    print(f"Waiting for {total_wait} seconds")
    time.sleep(1)
    total_wait -= 1
    if total_wait == 0:
        wait = False


# Circle parameters
center_x, center_y = pyautogui.position()  # Use current mouse position as center
radius = 100
steps = 120  # Number of points for smoother circle

# Move to starting point of the circle BEFORE pressing mouse down
start_x = center_x + radius
start_y = center_y
pyautogui.moveTo(start_x, start_y)

# Now start drawing the circle
pyautogui.mouseDown()
for i in range(steps + 1):
    angle = 2 * math.pi * i / steps
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    pyautogui.moveTo(x, y, duration=0.01)  # Small delay for smooth movement
pyautogui.mouseUp()
