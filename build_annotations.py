import json

# files to collect 
hasty_file_names = [
    "final_annotations/Gal_asc_letter_annotation_frenchandgerman_hastyformat.json",
    "final_annotations/Gal_extra_asc_final_annotations_german_030_Hastyformat.json",
    "final_annotations/Omer_asc_letter_annotation_hastyformat.json",
    "final_annotations/Sharva_asc_letter_annotation_hastyformat.json",
]

coco_file_names = [
    "final_annotations/Daria_Berat_final_asc_letter_annotation_hastyformat.json",
]

# info 
info = {
    "year": 2025,
    "date_created": "2025-01-24T01:00:14Z",
    "version": "1.0",
    "description": "hebrew_letter_annotation",
    "contributor": "",
    }

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
    }
]


curr_annotation_id = 0


result = {
    'info': info.copy(),
    'licenses': [],
    'categories': categories.copy(),
    'images': [],
    'annotations': [],
}

def map_image_id(image_name):
    image_name = image_name.split('.')[0]
    x, y, z = image_name.split('_')
    return int(x) * 100 + int(y) * 10 + int(z) 

def get_category_id(class_name):
    for category in categories:
        if class_name == "Alef":
            class_name = "Aleph"
        if class_name == "Shein":
            class_name = "Shin"
        if category['name'].lower().replace(' ', '') == class_name.lower().replace(' ', ''):
            return category['id']
    return -1

def convert_hasty_bbox_to_coco_bbox(hasty_bbox):
    if len(hasty_bbox) == 4:
        x_tl, y_tl, x_br, y_br = map(int, hasty_bbox)   
        width = x_br - x_tl
        height = y_br - y_tl
        coco_bbox = [x_tl, y_tl, width, height]
        return coco_bbox
    else: 
        return []
        

def map_image_labels(labels, curr_image_id):
    global curr_annotation_id
    annotations = []
    for label in labels:
        bbox = label.get('bbox',[])
        
        bbox = convert_hasty_bbox_to_coco_bbox(bbox)
        class_name = label.get('class_name')
        category_id = get_category_id(class_name)
        if len(bbox) !=4:
            area = 0
        else: 
            area = bbox[2] * bbox[3]
        annotations.append(
            {
                'id': curr_annotation_id,
                'image_id': curr_image_id,
                'category_id': category_id,
                'bbox': bbox,
                'area': area,
                'iscrowd': 0,
                'segmentation': None,
            }
        )
        curr_annotation_id += 1
    return annotations

# Hasty json1.1 files 
for file_name in hasty_file_names:
    with open(file_name, "r") as f:
        data = json.load(f)
    images = data.get('images', [])
    for image in images:
        image_name = image.get('image_name')
        image_width = image.get('width')
        image_height = image.get('height')
        image_labels = image.get('labels')
        
        result['images'].append(
            {
                'id': map_image_id(image_name),
                'file_name': image_name,
                'width': image_width,
                'height': image_height,
                'license': None,
                'flickr_url': "",
                'coco_url': None,
            }
        )

        result['annotations'].extend(map_image_labels(image_labels, map_image_id(image_name)))

# COCO files 
for file_name in coco_file_names:
    with open(file_name, "r") as f:
        data = json.load(f)
    images = data.get('images', [])
    annotations = data.get('annotations', [])
    annotations_by_image = {}
    old_to_new_image_id = {}
    for image in images:
        image_name = image.get('file_name')
        image_width = image.get('width')
        image_height = image.get('height')
        image_id = image.get('id')
        old_to_new_image_id[image_id] = map_image_id(image_name)
        result['images'].append(
            {
                'id': map_image_id(image_name),
                'file_name': image_name,
                'width': image_width,
                'height': image_height,
                'license': None,
                'flickr_url': "",
                'coco_url': None,
            }
        )
        annotations_by_image[image.get('id')] = []
    for annotation in annotations:
        annotations_by_image[annotation['image_id']].append(
            {
                'id': curr_annotation_id,
                'image_id': old_to_new_image_id[annotation['image_id']],
                'category_id': annotation['category_id'],
                'bbox': annotation['bbox'],
                'area': annotation['area'],
                'iscrowd': 0,
                'segmentation': None,

            }
        )
        curr_annotation_id += 1
    for annotations in annotations_by_image.values():
        result['annotations'].extend(annotations)


annotations_output_filename = 'annotations.json'


with open( annotations_output_filename , 'w') as f:
    json.dump(result, f, indent=4)

print(f"The annotation file, {annotations_output_filename}, was successfuly created.")