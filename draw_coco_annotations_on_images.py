import os
import json
import argparse
import cv2
import matplotlib.pyplot as plt
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

def draw_annotations(image, annotations):
    """
    Draws the COCO annotations on the image.
    """
    for ann in annotations:
        if 'bbox' in ann:
            x_tl, y_tl, w, h = map(int, ann['bbox'])

            # Draw the bounding box
            cv2.rectangle(image, (x_tl, y_tl), (x_tl + w, y_tl + h), (255, 0, 0), 1)

    return image

def show_cropped_annotations(images_path="cropped_annotations/3/"):
    # draw the cropped annotations with their names on rows and columns
    fig, axs = plt.subplots(len(images_path), 3, figsize=(15, 10))
    for image_path in images_path:
        image = cv2.imread(image_path)
        axs[0].imshow(image)
        axs[0].axis('off')
        axs[0].set_title('Original Image')
        axs[1].imshow(annotated_image)
        axs[1].axis('off')
        axs[1].set_title('Annotated Image')
        axs[2].imshow(cropped_image)
        axs[2].axis('off')
        axs[2].set_title('Cropped Image')
    plt.show()

    show_cropped_annotations()


def cropped_annotations(image, annotations,image_id,output_dir):
    """
    croppes the COCO annotations from the image .
    """
   
    for ann in annotations:
        image_id = ann.get('image_id')
        id = ann.get('id')
        category_id = ann.get('category_id')
        catergory_path = os.path.join(output_dir, f'{category_id}')
        os.makedirs(catergory_path, exist_ok=True)
        image_path = os.path.join(catergory_path, f'{category_id}_{image_id}_{id}_cropped.jpg')
        if 'bbox' in ann:
            x_tl, y_tl, w, h = map(int, ann['bbox'])
            cropped_image = image[y_tl:y_tl+h, x_tl:x_tl+w]
            cv2.imwrite(image_path, cropped_image)

def main(annotations_path, images_dir, output_dir, draw, crop, show_annotated_image):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load COCO annotations
    with open(annotations_path, 'r') as f:
        coco_data = json.load(f)

    images = coco_data.get('images', [])
    annotations = coco_data.get('annotations', [])

    # Create a mapping of image_id to annotations
    annotations_by_image = {}
    for ann in annotations:
        image_id = ann.get('image_id')
        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []
        annotations_by_image[image_id].append(ann)

    # Process each image
    for image_info in images: # per each main region in the image
        image_id = image_info.get('id')
        file_name = image_info.get('file_name')
        manuscript_id = file_name[:file_name.find('.')][:-3]
        image_path = os.path.join(os.path.join(images_dir, manuscript_id) ,file_name)
        print(f"Processing image {image_path}...")
        if not os.path.exists(image_path):
            print(f"Image {file_name} not found in {images_dir}, skipping.")
            continue

        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read {image_path}, skipping.")
            continue

        # Get annotations for this image
        image_annotations = annotations_by_image.get(image_id, [])
        if crop:
            cropped_annotations(image, image_annotations,image_id,output_dir)
        # Draw annotations
        if draw:
            annotated_image = draw_annotations(image.copy(), image_annotations)
            if show_annotated_image:
                cv2.imshow("Annotated Image", annotated_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_annotated.jpg")
            cv2.imwrite(output_path, annotated_image)
            print(f"Annotated image saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw COCO annotations on images and save them.")
    parser.add_argument("--annotations", required=True, help="Path to the COCO annotations JSON file.")
    parser.add_argument("--images_dir", required=True, help="Path to the directory containing the images.")
    parser.add_argument("--output_dir", required=True, help="Path to the directory to save annotated images.")
    parser.add_argument("--draw", action="store_true", help="Show the annotated images.")
    parser.add_argument("--crop", action="store_true", help="Crop the annotated images and save them.")
    parser.add_argument("--show_annotated_image", action="store_true", help="Show the cropped images.")
    args = parser.parse_args()
    main(args.annotations, args.images_dir, args.output_dir, args.draw, args.crop, args.show_annotated_image)
    