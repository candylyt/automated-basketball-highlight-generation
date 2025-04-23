import cv2 
import json
import os

run_id = '0a08da5c-1a73-4a01-87e5-7969834cff9b'
court_img = 'resources/court_map.jpg'
json_file_path = f'data/{run_id}.json'
output_path = f'plots/{run_id}'
os.makedirs(output_path, exist_ok=True)

with open(json_file_path, 'r') as f:
    data = json.load(f)
    shot_data = None
    # print(data.get('is_match') == True)
    if data.get('is_match', False):
        shot_data = data.get('team_A', {}).get('shot_data', []) + data.get('team_B', {}).get('shot_data', [])
    else:
        shot_data = data.get('shot_data', [])
        
    print(shot_data)

    # print(data.get('team_A', {}).get('shot_data', []) + data.get('team_B', {}).get('shot_data', []))
    
    for shot in shot_data:
        x, y = shot['x'], shot['y']
        if x and y:
            img = cv2.imread(court_img)
            cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1)
            timestring = shot['timestamp'].replace(':', '-')

            cv2.imwrite(os.path.join(output_path, timestring+'.jpg'), img)
    