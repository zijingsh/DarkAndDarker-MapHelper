
import cv2
import mss
from PIL import Image
import numpy as np
import time
import json
import math

with open('Crypt.json', 'r') as json_file:
    data = json.load(json_file)
with open('ItemGroups.json', 'r') as json_file:
    item_data = json.load(json_file)
# record video of screen using cv2
fps = 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (2560, 1440))
mon = {'left': 0, 'top': 0, 'width': 2560, 'height': 1440}


map_unfound = cv2.imread('Crypt_06.png')
map_found = map_unfound # Assign default value
map_unfound_grey = cv2.cvtColor(map_found, cv2.COLOR_BGR2GRAY)

MIN_CONFIDENCE = 0.55
map_count = 1
resized = False

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Draw a blue dot at the clicked location
        cv2.circle(map_found, (x, y), 5, (255, 0, 0), -1)

        # Log the coordinates of the click
        print(f'Clicked at ({x}, {y})')

def transform (point, map, scale = 1):
    h, w, _ = map.shape
    x, y = point
    x = scale * (1 * x + 0)
    y = scale  * (1 * y + 0)
    
    x = w - x *2
    y = h - y*2
    y = h - y
    return (x, y)

with mss.mss() as sct:
    detected_location = False

    while True:
        img = sct.grab(mon)
        frame = Image.frombytes(
            'RGB', 
            (img.width, img.height), 
            img.rgb, 
        )
        frame = np.array( frame)
        out.write(frame)

        # Resize the frame, Convert to grayscale. 1440p 
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
        frame = frame[1160:1380, 2240:2460]
        
        frame = cv2.resize(frame, (int(frame.shape[1] * 0.8), int(frame.shape[0] * 0.8)))
        
        if not(detected_location):
        
            if(map_count < 6):
                map_count += 1
            else:
                map_count = 1
            map_unfound = cv2.imread(f'Crypt_0{map_count}.png')
            map_unfound_grey = cv2.cvtColor(map_unfound, cv2.COLOR_BGR2GRAY)
            map_unfound = cv2.resize(map_unfound, (1100,1100))
            map_unfound = map_unfound[86:1010, 87:1002]
            map_unfound = cv2.resize(map_unfound, (690,690))
            map_unfound_grey = cv2.cvtColor(map_unfound, cv2.COLOR_BGR2GRAY)
            resized = True

        else:
            MIN_CONFIDENCE = 0.32
            map_found = map_unfound
            
            cv2.imshow('map ' + str(map_count), map_found)
            if "map" + str(map_count) in data:
                    for entry in data["map" + str(map_count)]:

                        entry_id = entry.get("id")
                        coordinates = entry.get("coordinates")

                        lat, lng = transform((coordinates["lat"], coordinates["lng"]), map_found)
                        lat += 50; lng -= 55
                        

                        for item in item_data["Golden Chest"]:
                            if(entry_id == item):
                                cv2.circle(map_found, (int(lng), int(lat)), 5, (23, 229, 232), -1)
                                break
                        if(entry_id == "Id_Spawner_Props_Statue01"):
                            cv2.circle(map_found, (int(lng), int(lat)), 5, (65, 232, 23), -1)
                        if(entry_id == "BP_CryptEscape"):
                            cv2.circle(map_found, (int(lng), int(lat)), 5, (232, 159, 23), -1)
                        #if(entry_id == "SpawnPoint"):
                            #cv2.circle(map_found, (int(lng), int(lat)), 5, (245, 27, 238), -1)
            cv2.setMouseCallback('map ' + str(map_count), click_event)
        
        result = cv2.matchTemplate(map_unfound_grey, frame, cv2.TM_CCOEFF_NORMED)

        if (result.max() > MIN_CONFIDENCE):  
            detected_location = True
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                # Draw player's location on reference map
            cv2.circle(
                map_found, 
                (int(max_loc[0] + 25 + frame.shape[1] / 2),
                int(max_loc[1] - 25 + frame.shape[0] / 2)),
                5, (0, 0, 255), -1)

        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1/fps)

out.release()

