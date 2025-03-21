

import os
import json
import argparse
import cv2
import matplotlib.pyplot as plt

INPUT_FILE_PATH = r"wrong-image-classes"


categories = [
    {
        "id": 1,
        "name": "Aleph",
        "supercategory": "object"
    },
    {
        "id": 2,
        "name": "He",
        "supercategory": "object"
    },
    {
        "id": 3,
        "name": "Mem",
        "supercategory": "object"
    },
    {
        "id": 4,
        "name": "Shin",
        "supercategory": "object"

    },
        {
        "id": 5,
        "name": "Mem Sofit",
        "supercategory": "object"
    },
    {
        "id": 6,
        "name": "Tav",
        "supercategory": "object"
    }, 
]
def extract_image_id__id(image_name):
    image_id =int(image_name.split('_')[1])
    annotation_id = int(image_name.split('_')[2])
    return image_id ,annotation_id
   

def map_catergory_name_to_id(category_name):
    for category in categories:
        category_name = category_name.split(".")[0].strip().title()
        if category["name"] == category_name:
            return category["id"]
    return -1

wrong_annotations = []

for file in os.listdir(INPUT_FILE_PATH):
    category = int(file.split("_")[-1].split(".")[0])
    script_mode = file.split("_")[0]
    with open(os.path.join(INPUT_FILE_PATH,file), "r") as f:
        data = f.readlines()
    for line in data:
        image_name, correct_class_name = line.strip().split(":")
        correct_class_name = correct_class_name.strip().title()
        image_id, annotation_id = extract_image_id__id(image_name)
        correct_class_name_id = map_catergory_name_to_id(correct_class_name)
        if correct_class_name in ["He?", "Cut"]:
            continue
        
        wrong_annotations.append({
            "image_id": image_id,
            "id": annotation_id,
            "correct_category_name": correct_class_name,
            "correct_category_id": correct_class_name_id, 
            "old_category": category,
        }) 

    with open(f"wrong_annotations.json", "w") as f:
        json.dump(wrong_annotations, f, indent=4)

    print(f"Saved {len(wrong_annotations)} wrong annotations to wrong_annotations.json")
    
    print("Done")
