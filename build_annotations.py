import json

hasty_file_names = [
    "final_annotations/Gal_asc_letter_annotation_frenchandgerman_hastyformat.json",
    "final_annotations/Gal_extra_asc_final_annotations_german_030_Hastyformat.json",
    "final_annotations/Omer_asc_letter_annotation_hastyformat.json",
    "final_annotations/Sharva_asc_letter_annotation_hastyformat.json",
]

coco_file_names = [
    "final_annotations/Daria_Berat_final_asc_letter_annotation_hastyformat.json",
    "final_annotations/annotations_french.json",
    "final_annotations/annotations_german.json"
]

categories = [
    {
        "id": 1,
        "name": "Aleph"
    },
    {
        "id": 2,
        "name": "He"
    },
    {
        "id": 3,
        "name": "Mem"
    },
    {
        "id": 4,
        "name": "Shin"
    },
        {
        "id": 5,
        "name": "Mem Sofit"
    },
    {
        "id": 6,
        "name": "Tav"
    }
]


curr_annotation_id = 0


result = {
    'images': [],
    'annotations': [],
    'categories': categories.copy()
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


def map_image_labels(labels, curr_image_id):
    global curr_annotation_id
    annotations = []
    for label in labels:
        bbox = label.get('bbox')
        class_name = label.get('class_name')
        category_id = get_category_id(class_name)
        area = bbox[2] * bbox[3]
        annotations.append(
            {
                'id': curr_annotation_id,
                'image_id': curr_image_id,
                'category_id': category_id,
                'bbox': bbox,
                'area': area,
                'iscrowd': 0
            }
        )
        curr_annotation_id += 1
    return annotations


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
                'height': image_height
            }
        )
        result['annotations'].extend(map_image_labels(image_labels, map_image_id(image_name)))


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
                'height': image_height
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
                'iscrowd': 0
            }
        )
        curr_annotation_id += 1
    for annotations in annotations_by_image.values():
        result['annotations'].extend(annotations)


with open('annotations.json', 'w') as f:
    json.dump(result, f, indent=4)