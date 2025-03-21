
## Build the annotations.json
In order to create the annotation.json file 
run the file: `build_annotations.py`
using the command: 
```
python build_annotations.py
```
- Notice: Adjust the FIX_ANNOTATIONS_FLAG param as needed:
    -- FIX_ANNOTATIONS_FLAG = True, assumming that:
        1) `wrong_annotations.json` exists 
        2) and is in the same directory as this script.
    -- FIX_ANNOTATIONS_FLAG = False, doesn't fix wrong categories of the raw annotations files. 



## Fix Raw annotations 
Running the file `aggregate_save _wrong_annotations.py` assumes that the directory `wrong-image-classes` exists.
It iterates over the files in this directory and creates an aggregated json file `wrong_annotations.json`.

## Crop the Images according to the annotations.json and save them 
For example, run this command: 
```
python draw_coco_annotations_on_images.py --annotations annotations.json --images_dir images/french/ --output_dir cropped_annotations/french --crop
```
### Review the Cropped Images 
For example, run this command: 
```
python review_cropped_letters.py --script_mode french --category_id 1
```

## Draw the Images according to the annotations.json and save them 
For example, run this command: 
```
python draw_coco_annotations_on_images.py --annotations annotations.json --images_dir images/french/ --output_dir cropped_annotations/french --draw 
``` 
use --show_annotated_image to show each annotated image. 
