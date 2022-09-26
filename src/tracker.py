import numpy as np
from window_capture import WindowCapture
import pytesseract
import matplotlib.pyplot as plt
import ctypes, re, time

awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

capture_period = 1.0

# WindowCapture.list_window_names()

quest_y = 0.19
quest_h = 0.09
quest_x = 0.25
complete_y = 0.235
complete_h = 0.08
complete_x = 0.71
complete_w = 0.17

def sanitize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z ]", "", text)
    text = text.strip()
    return text 

window_name = 'Windowed Projector (Source) - Capture Card'
# window_name = 'Picture-in-Picture'

wincap = WindowCapture(window_name=window_name)

next_time = time.monotonic()
while True:
    frame = wincap.get_screenshot()
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    quest_img = frame[int(quest_y * frame_h):int((quest_y + quest_h) * frame_h),
                    int(quest_x * frame_w):-int(quest_x * frame_w)]

    quest_text = pytesseract.image_to_string(quest_img)
    quest_text = sanitize_text(quest_text)
    print(quest_text)

    complete_img = frame[int(complete_y * frame_h):int((complete_y + complete_h) * frame_h),
                        int(complete_x * frame_w):int((complete_x + complete_w) * frame_w)]

    complete_text = pytesseract.image_to_string(complete_img)
    complete_text = sanitize_text(complete_text)

    print(complete_text)
    if complete_text == 'complete' and quest_text != '':
        print('Completed ' + quest_text + '!')

    next_time += capture_period
    sleep_time = next_time - time.monotonic()

    if sleep_time < 0:
        next_time = time.monotonic()
    else:
        time.sleep(sleep_time)

