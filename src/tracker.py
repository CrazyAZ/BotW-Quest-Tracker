import numpy as np
from window_capture import WindowCapture
from utils import *
import pytesseract
import ctypes, time
import matplotlib.pyplot as plt

awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

capture_period = 0.5

quest_y = 0.19
quest_h = 0.09
quest_x = 0.23
complete_y = 0.235
complete_h = 0.08
complete_x = 0.71
complete_w = 0.17

complete_threshold = 0.6
quest_threshold = 0.85

second_viewing_interval = 6.0

window_name = WindowCapture.find_window_name('Windowed Projector (Source)')
# window_name = 'Picture-in-Picture'

main_quests = []
with open('data/main_quests.txt', 'r', encoding="utf-8") as file:
    for quest in file:
        main_quests.append(sanitize_text(quest))

shrine_quests = []
with open('data/shrine_quests.txt', 'r', encoding="utf-8") as file:
    for quest in file:
        shrine_quests.append(sanitize_text(quest))

side_quests = []
with open('data/side_quests.txt', 'r', encoding="utf-8") as file:
    for quest in file:
        side_quests.append(sanitize_text(quest))

all_quests = [main_quests, shrine_quests, side_quests]

last_seen = [[None for _ in range(len(all_quests[i]))] for i in range(3)]

quest_totals = np.empty(3, dtype='uint8')
for i in range(3):
    quest_totals[i] = len(all_quests[i])
quests_completed = np.zeros_like(quest_totals)

def write_remaining_quests_to_file():
    with open('tmp/remaining_quests.txt', 'w', encoding="utf-8") as file:
        file.write('Main Quests:\n')
        for quest in all_quests[0]:
            file.write(quest + '\n')

        file.write('\nShrine Quests:\n')
        for quest in all_quests[1]:
            file.write(quest + '\n')

        file.write('\nSide Quests:\n')
        for quest in all_quests[2]:
            file.write(quest + '\n')

write_remaining_quests_to_file()

def quest_completed(quest_type, quest_index):
    quest = all_quests[quest_type][quest_index]
    quests_completed[quest_type] += 1

    print('Completed ' + quest + '!')
    print(quests_completed[0], '/', quest_totals[0], quests_completed[1], '/', quest_totals[1], quests_completed[2], '/', quest_totals[2])

    del all_quests[quest_type][quest_index]
    del last_seen[quest_type][quest_index]

    write_remaining_quests_to_file()


wincap = WindowCapture(window_name=window_name)

next_time = time.monotonic()
while True:
    next_time += capture_period
    sleep_time = next_time - time.monotonic()
    
    if sleep_time < 0:
        next_time = time.monotonic()
    else:
        time.sleep(sleep_time)

    frame = wincap.get_screenshot()
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    quest_img = frame[int(quest_y * frame_h):int((quest_y + quest_h) * frame_h),
                          int(quest_x * frame_w):-int(quest_x * frame_w)] < 60

    quest_text = pytesseract.image_to_string(quest_img)
    quest_text = sanitize_text(quest_text)

    if quest_text == '':
        continue

    all_scores = []
    for i in range(3):
        quest_list = all_quests[i]
        scores = np.empty(len(quest_list))
        for q in range(len(quest_list)):
            scores[q] = match_percentage(quest_text, quest_list[q])
        all_scores.append(scores)
        
    top_scores = np.empty(3)
    for i in range(3):
        top_scores[i] = np.amax(all_scores[i])
    
    quest_type = np.argmax(top_scores)
    top_score = np.amax(top_scores)

    if top_score < quest_threshold:
        continue

    quest_index = np.argmax(all_scores[quest_type])
    quest = all_quests[quest_type][quest_index]

    # print(quest, top_score)

    if last_seen[quest_type][quest_index] is None:
        last_seen[quest_type][quest_index] = time.monotonic()
    elif time.monotonic() - last_seen[quest_type][quest_index] > second_viewing_interval:  # Quest banner seen twice
        quest_completed(quest_type, quest_index)
        continue

    complete_img = frame[int(complete_y * frame_h):int((complete_y + complete_h) * frame_h),
                        int(complete_x * frame_w):int((complete_x + complete_w) * frame_w)]

    complete_text = pytesseract.image_to_string(complete_img)
    complete_text = sanitize_text(complete_text)

    if complete_text != '' and match_percentage(complete_text, 'complete') > complete_threshold:  # "Complete" text seen
        quest_completed(quest_type, quest_index)

