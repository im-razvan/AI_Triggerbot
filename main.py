import torch, mss
from ultralytics import YOLO
import win32api, win32con
from icecream import ic
import numpy as np
from time import sleep

# ==================================

MODEL = 'models/yolo11s.pt'
STOP_KEY = win32con.VK_F1
STOPPED = True

# ==================================

CUDA = torch.cuda.is_available()

ic(f"CUDA status: {CUDA}")

device = torch.device("cuda" if CUDA else "cpu")
model = YOLO(MODEL, task='detect')
model.to(device=device)

sct = mss.mss()
screen_width, screen_height = sct.monitors[1]['width'], sct.monitors[1]['height']
crosshair_x, crosshair_y = screen_width // 2, screen_height // 2

ALPHA = round(
    screen_width * screen_height * 100 / (2560*1440)
) # magic

ic(f"ALPHA value: {ALPHA}")

def capture_screen():
    monitor = {
        "top": crosshair_y - ALPHA,
        "left": crosshair_x - ALPHA,
        "width": 2*ALPHA,
        "height": 2*ALPHA
    }

    screenshot = sct.grab(monitor)
    return np.array(screenshot)[:, :, :3] # remove alpha

def check_stop():
    key_state = win32api.GetAsyncKeyState(STOP_KEY)
    global STOPPED
    pressed = bool(key_state & 0x8000)
    if pressed == True:
        STOPPED = not STOPPED
        ic(f"{STOPPED=}")
        sleep(0.3)

def click():
    x, y = win32api.GetCursorPos()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def triggerbot():
    frame = capture_screen()
    results = model(frame, verbose=False)
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if cls_id == 0: # Class id for person
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # ic(x1,y1,x2,y2)
                if x1 <= ALPHA <= x2 and y1 <= ALPHA <= y2:
                    click()
                    sleep(0.1)
                    return
                
def main():
    ic(f"{STOPPED=}")
    ic("The game should have the same resolution as the screen!")
    while True:
        try:
            check_stop()
            if not STOPPED:
                triggerbot()

            sleep(0.02)
        except KeyboardInterrupt:
            ic("Bye!")
            break
        except Exception as e:
            ic(e)
            pass

if __name__ == '__main__':
    main()