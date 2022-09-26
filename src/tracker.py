import numpy as np
from window_capture import WindowCapture
from utils import *
import pytesseract
import matplotlib.pyplot as plt
import ctypes, time

awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

capture_period = 1.0

quest_y = 0.19
quest_h = 0.09
quest_x = 0.23
complete_y = 0.235
complete_h = 0.08
complete_x = 0.71
complete_w = 0.17

complete_threshold = 0.6
quest_threshold = 0.6

window_name = WindowCapture.find_window_name('Windowed Projector (Source)')
# window_name = 'Picture-in-Picture'

file = open('data/main_quests.txt', 'r')
main_quests = []
for quest in file:
    main_quests.append(sanitize_text(quest))
file.close()

file = open('data/shrine_quests.txt', 'r')
shrine_quests = []
for quest in file:
    shrine_quests.append(sanitize_text(quest))
file.close()

file = open('data/side_quests.txt', 'r')
side_quests = []
for quest in file:
    side_quests.append(sanitize_text(quest))
file.close()

all_quests = [main_quests, shrine_quests, side_quests]

quest_totals = np.empty(len(all_quests), dtype='uint8')
for i in range(len(all_quests)):
    quest_totals[i] = len(all_quests[i])
quests_completed = np.zeros_like(quest_totals)


wincap = WindowCapture(window_name=window_name)

next_time = time.monotonic()
while True:
    frame = wincap.get_screenshot()
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    complete_img = frame[int(complete_y * frame_h):int((complete_y + complete_h) * frame_h),
                        int(complete_x * frame_w):int((complete_x + complete_w) * frame_w)]

    complete_text = pytesseract.image_to_string(complete_img)
    complete_text = sanitize_text(complete_text)

    if complete_text != '' and match_percentage(complete_text, 'complete') > complete_threshold:
        quest_img = frame[int(quest_y * frame_h):int((quest_y + quest_h) * frame_h),
                          int(quest_x * frame_w):-int(quest_x * frame_w)]

        quest_text = pytesseract.image_to_string(quest_img)
        quest_text = sanitize_text(quest_text)

        all_scores = []
        for i in range(len(all_quests)):
            quest_list = all_quests[i]
            scores = np.empty(len(quest_list))
            for q in range(len(quest_list)):
                scores[q] = match_percentage(quest_text, quest_list[q])
            all_scores.append(scores)
            
        top_scores = np.empty(len(all_scores))
        for i in range(len(all_scores)):
            top_scores[i] = np.amax(all_scores[i])
        
        quest_type = np.argmax(top_scores)

        quest_index = np.argmax(all_scores[quest_type])
        quest = all_quests[quest_type][quest_index]
        quests_completed[quest_type] += 1

        print('Completed ' + quest + '! Score:', all_scores[quest_type][quest_index])
        print(quests_completed[0], '/', quest_totals[0], quests_completed[1], '/', quest_totals[1], quests_completed[2], '/', quest_totals[2])
    
        del all_quests[quest_type][quest_index]

        next_time += 2.0
    elif complete_text != '':
        print(complete_text, match_percentage(complete_text, 'complete'))

    next_time += capture_period
    sleep_time = next_time - time.monotonic()

    if sleep_time < 0:
        next_time = time.monotonic()
    else:
        time.sleep(sleep_time)

