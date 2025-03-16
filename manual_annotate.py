import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk
import json
import os
import sys
import os
import sys


# Define the categories
CATEGORIES = [
    {"id": 1, "name": "Aleph"},
    {"id": 2, "name": "He"},
    {"id": 3, "name": "Mem"},
    {"id": 4, "name": "Shin"},
    {"id": 5, "name": "Mem Sofit"},
    {"id": 6, "name": "Tav"},
]

class CategorySelectionDialog(tk.Toplevel):
    def __init__(self, parent, title, message, categories):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.choice = None

        # Center the dialog over the parent window
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")

        # Message Label
        tk.Label(self, text=message, wraplength=300, justify="left").pack(pady=10, padx=10)

        # Category Options
        self.category_var = tk.StringVar(value=categories[0]["name"])

        for category in categories:
            tk.Radiobutton(
                self, text=category["name"], variable=self.category_var, value=category["name"]
            ).pack(anchor=tk.W, padx=20)

        # OK and Cancel buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window()

    def on_ok(self):
        self.choice = self.category_var.get()
        self.destroy()

    def on_cancel(self):
        self.choice = None
        self.destroy()

class OptionDialog(tk.Toplevel):
    def __init__(self, parent, title, message, options):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.choice = None

        # Center the dialog over the parent window
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")

        # Message Label
        tk.Label(self, text=message, wraplength=300, justify="left").pack(pady=10, padx=10)

        # Option Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        for opt in options:
            btn = tk.Button(button_frame, text=opt, width=15, command=lambda opt=opt: self.set_choice(opt))
            btn.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.wait_window()

    def set_choice(self, choice):
        self.choice = choice
        self.destroy()

    def on_close(self):
        self.choice = None
        self.destroy()

class BoundingBoxEditor:
    def __init__(self, root):
        self.dragging = False
        self.editing_enabled = False
        self.root = root
        self.root.title("Bounding Box Editor")

        # Initialize variables
        self.image = None
        self.drawn_image = None
        self.tk_image = None
        self.canvas = None
        self.rect = None
        self.start_x = self.start_y = 0
        self.bboxes = []
        self.annotations = []
        self.annotation_id = 1
        self.image_id = None
        self.file_path = ''
        self.json_path = ''
        self.script_mode = ""
        self.coco_data = {
            "images": [],
            "annotations": [],
            "categories": CATEGORIES.copy()
        }
        self.selected_category_id = None
        self.selected_category_name = None
        self.scale_factor = 1

        # Load image and annotations
        self.load_image_and_annotations()
        
    def load_image_and_annotations(self):
        # Ask user to select an image file
        self.file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if not self.file_path:
            messagebox.showerror("Error", "No image selected.")
            self.root.quit()
            return

        # Load the image
        self.image = Image.open(self.file_path)
        self.drawn_image = self.image.copy()
        self.tk_image = ImageTk.PhotoImage(self.drawn_image)

        # Create a frame to hold the canvas and scrollbars
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the scrollbars with the canvas
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Bind Shift + MouseWheel for horizontal scrolling
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mouse_wheel)

        # Bind scrolling on mousewheel
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Display the image on the canvas
        self.image_container = self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        # Set the scroll region to match the image dimensions
        self.canvas.config(scrollregion=(0, 0, self.tk_image.width(), self.tk_image.height()))

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Buttons for scaling up/down
        self.scale_up_button = tk.Button(self.root, text="Scale Up", command=self.scale_up)
        self.scale_up_button.pack(side=tk.RIGHT)

        self.scale_down_button = tk.Button(self.root, text="Scale Down", command=self.scale_down)
        self.scale_down_button.pack(side=tk.RIGHT)

        # Extract the file name and set JSON path
        self.image_file_name = os.path.basename(self.file_path)
        self.select_script_mode()
        self.json_path = self.get_annotations_file_path()

        # Calculate image ID
        self.image_id = self.calculate_image_id()

        # Ask the user to select a category
        self.select_category()

        self.load_annotations()
        if self.image_exists_in_annotations(self.image_file_name):
            if self.image_contains_category_annotations(self.image_id, self.selected_category_id):
                self.handle_existing_annotations()
            else:
                # No existing annotations for that category, setup new annotations
                self.setup_new_annotations()
        else:
            self.add_image_info()
            self.setup_new_annotations(start_over=True)

        self.set_screen_size_dynamically()

    def get_next_annotation_id(self):
        if self.coco_data["annotations"]:
            # Extract all existing IDs and sort them
            ids = list(set(sorted(ann["id"] for ann in self.coco_data["annotations"])))

            # Find the first missing positive integer
            for idx, id_value in enumerate(ids, start=1):
                if id_value != idx:
                    return idx

            # If no gaps, return the next ID after the max
            return ids[-1] + 1
        return 1

    def set_screen_size_dynamically(self):
        # Get image dimensions
        image_width, image_height = self.drawn_image.size

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set the window size (e.g., 80% of the screen size)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        window_width = min(window_width, image_width)
        window_height = min(window_height, image_height)

        # print(f"Image size: {image_width}x{image_height}")
        # print(f"Screen size: {screen_width}x{screen_height}")
        # print(f"Window size: {window_width}x{window_height}")

        # Center the window on the screen
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def on_shift_mouse_wheel(self, event):
        """Scroll horizontally with Shift + mouse wheel."""
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def on_mouse_wheel(self, event):
        """Scroll vertically with the mouse wheel."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def select_category(self):
        dialog = CategorySelectionDialog(
            self.root,
            "Select Category",
            "Please select the category you want to work with:",
            CATEGORIES
        )
        category_name = dialog.choice
        if category_name is None:
            # User cancelled
            self.root.quit()
            return
        # Find the category id
        for category in CATEGORIES:
            if category["name"] == category_name:
                self.selected_category_id = category["id"]
                self.selected_category_name = category_name
                break

    def handle_existing_annotations(self):
        # Create custom dialog with options
        options = ["View Annotations", "Start Over", "Edit Annotations"]
        dialog = OptionDialog(
            self.root,
            "Existing Annotations Found",
            f"Annotations for this image already exist in category '{self.selected_category_name}'. What would you like to do?",
            options
        )
        response = dialog.choice

        if response == "View Annotations":
            # View annotations
            self.display_image_with_boxes()
        elif response == "Start Over":
            # Start over
            self.add_image_info()
            self.setup_new_annotations(start_over=True)
        elif response == "Edit Annotations":
            # Edit annotations
            self.display_image_with_boxes()
            self.enable_editing()
        else:
            # User closed the dialog or pressed cancel
            self.root.quit()

    def select_script_mode(self):
        # Create custom dialog with options
        options = ["French", "German"]

        # Break file path into directory components
        dir_components = os.path.normpath(self.file_path).split(os.sep)

        # Filter options to exclude those already in the directory list
        filtered_options = [option for option in options if option.lower() in map(str.lower, dir_components)]

        # If the language is in the path, choose it automatically
        if len(filtered_options) != 0:
            response = filtered_options[0]
        else:
            dialog = OptionDialog(
                self.root,
                "Please Select Script Mode",
                "Please select the Script mode you want to annotate for!",
                options
            )
            response = dialog.choice

        if response == "French":
            self.script_mode = "french"
        elif response == "German":
            self.script_mode = "german"
        else:
            # User closed the dialog or pressed cancel
            self.root.quit()

    def create_annotations_file(self):
        # Prompt the user to select a directory
        dir_path = filedialog.askdirectory(title="Select Directory")
        if not dir_path:
            messagebox.showinfo("Operation Cancelled", "No directory selected. Exiting.")
            return
        
        # Prompt the user to enter a filename, with a default value
        default_name = f"annotations_{self.script_mode}"
        file_name = simpledialog.askstring("Input", "Enter the annotations file name (without extension):", initialvalue=default_name)
        if not file_name:
            messagebox.showinfo("Operation Cancelled", "No file name entered. Exiting.")
            return
        
        # Add .json extension if not provided
        if not file_name.endswith(".json"):
            file_name += ".json"
        
        # Create the full path
        full_path = os.path.join(dir_path, file_name)
        
        # Create the JSON file
        try:
            with open(full_path, 'w') as json_file:
                json.dump(self.coco_data, json_file)
            # messagebox.showinfo("Success", f"File created at: {full_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the file:\n{e}")
        return full_path

    def get_annotations_file_path(self):
        options = ["New", "Existing"]
        dialog = OptionDialog(
            self.root,
            "New or Existing Annotations File?",
            "Please select whether you want to initialize new annotations file or continue to annotate in an existing one!",
            options
        )
        response = dialog.choice

        if response == "New":
            return self.create_annotations_file()
        elif response == "Existing":
            file_path = filedialog.askopenfilename(
                title="Select Annotations File",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )

            if not file_path:
                messagebox.showinfo("Operation Cancelled", "No file selected. Exiting.")
                return
            return file_path
        else:
            # User closed the dialog or pressed cancel
            self.root.quit()

    def add_image_info(self):
        # Add image info to COCO data
        if not self.image_exists_in_annotations(self.image_file_name):
            self.coco_data["images"].append({
                "id": self.calculate_image_id(),
                "file_name": self.image_file_name,
                "width": self.image.width,
                "height": self.image.height
            })
        # Ensure categories are set
        self.coco_data["categories"] = CATEGORIES.copy()
        self.image_id = self.calculate_image_id()

    def calculate_image_id(self):
        # Parse the file name to get the left, midle and right parts
        image_name, _ = os.path.splitext(self.image_file_name)
        left_part, middle_part, right_part = map(int, image_name.split("_"))
        # Calculate the new image ID
        new_image_id = left_part * 100 + middle_part * 10 + right_part
        return new_image_id

    def image_exists_in_annotations(self, image_file_name):
        return any(image_file_name == d["file_name"] for d in self.coco_data['images'])

    def image_contains_category_annotations(self, image_id, category_id):
        return any(image_id == d["image_id"] and category_id == d["category_id"] for d in self.coco_data['annotations'])

    def is_category_annotated(self):
        with open(self.json_path, 'r') as f:
            coco_data = json.load(f)

        # Check if the selected category is already annotated
        for ann in coco_data["annotations"]:
            if ann["category_id"] == self.selected_category_id:
                return True
        return False

    def fix_annotation_ids(self):
        seen_ids = set()
        for item in self.coco_data['annotations']:
            if item['id'] in seen_ids:
                item['id'] = self.get_next_annotation_id()
            else:
                seen_ids.add(item['id'])
        self.save_annotations()

    def load_annotations(self):
        # Load existing annotations from JSON
        with open(self.json_path, 'r') as f:
            self.coco_data = json.load(f)

        # Ensure categories are set
        self.coco_data.setdefault("categories", CATEGORIES.copy())

        # Find the image ID
        for img in self.coco_data["images"]:
            image_name = img["file_name"] 
            if image_name == self.image_file_name:
                self.image_id = img["id"]
                break

        # Load annotations of the selected category
        self.annotations = [
            ann for ann in self.coco_data["annotations"]
            if ann["image_id"] == self.image_id and ann["category_id"] == self.selected_category_id
        ]

        self.bboxes = [ann["bbox"] for ann in self.annotations]

        # Set annotation ID to max existing ID + 1
        self.annotation_id = self.get_next_annotation_id()

    def setup_new_annotations(self, start_over=False):
        # Remove existing annotations of the selected category
        if start_over:
            self.coco_data["annotations"] = [
                ann for ann in self.coco_data["annotations"]
                if not (ann["image_id"] == self.image_id and ann["category_id"] == self.selected_category_id)
            ]
        self.annotations = []
        self.bboxes = []
        # Set annotation ID to max existing ID + 1
        self.annotation_id = self.get_next_annotation_id()
        # Allow adding new annotations
        self.enable_editing()

    def display_image_with_boxes(self):
        # Draw bounding boxes on the image
        draw = ImageDraw.Draw(self.drawn_image)
        
        # Determine dynamic line width based on image size
        img_width, img_height = self.image.size
        line_width = max(2, int(min(img_width, img_height) * 0.001))  # 0.2% of the smaller dimension, minimum 2 pixels

        for bbox in self.bboxes:
            x, y, width, height = bbox
            x, y, width, height = x * self.scale_factor, y * self.scale_factor, width * self.scale_factor, height * self.scale_factor
            draw.rectangle([x, y, x + width, y + height], outline="red", width=line_width)

        # Update the canvas image
        self.tk_image = ImageTk.PhotoImage(self.drawn_image)
        self.canvas.itemconfig(self.image_container, image=self.tk_image)

    def enable_editing(self):
        # Add button for saving annotations
        self.save_button = tk.Button(self.root, text="Save Annotations", command=self.save_annotations)
        self.save_button.pack(side=tk.LEFT)
        self.editing_enabled = True

    def on_click(self, event):
        if not self.editing_enabled:
            return
        # Get the click coordinates
        click_x = self.canvas.canvasx(event.x)
        click_y = self.canvas.canvasy(event.y)

        # Check if the click is within any existing bounding box
        for idx, bbox in enumerate(self.bboxes):
            bx, by, bw, bh = bbox
            self.dragging = False
            if bx <= click_x <= bx + bw and by <= click_y <= by + bh:
                # Confirm deletion
                confirm = messagebox.askyesno("Delete Annotation", "Do you want to delete this annotation?")
                if confirm:
                    # Delete the annotation
                    self.bboxes.pop(idx)
                    ann_id = self.annotations.pop(idx)["id"]
                    # Remove from coco_data annotations
                    self.coco_data["annotations"] = [ann for ann in self.coco_data["annotations"] if ann["id"] != ann_id]
                    self.display_image_with_boxes()
                    self.annotation_id = self.get_next_annotation_id()
                    # Exit the function after handling the deletion
                return

        # If no bounding box was clicked, start drawing a new rectangle
        self.start_x = click_x
        self.start_y = click_y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")
        self.dragging = True  # Dragging starts

    def on_drag(self, event):
        if not self.editing_enabled:
            return
        # Update the rectangle as the mouse is dragged
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        if not self.editing_enabled:
            return
        if not self.dragging:
            return  # Don't finalize if not dragging    
        # Finalize the rectangle and save the annotation
        end_x, end_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        x, y = min(self.start_x, end_x), min(self.start_y, end_y)
        # Divide by the scale factor
        x_scaled, y_scaled = x / self.scale_factor, y / self.scale_factor
        width, height = abs(self.start_x - end_x), abs(self.start_y - end_y)
        # Divide by the scale factor
        width_scaled, height_scaled = width / self.scale_factor, height / self.scale_factor

        if width_scaled > 0 and height_scaled > 0:
            # Save the annotation
            annotation = {
                "id": self.annotation_id,
                "image_id": self.image_id,
                "category_id": self.selected_category_id,
                "bbox": [x_scaled, y_scaled, width_scaled, height_scaled],
                "area": width_scaled * height_scaled,
                "iscrowd": 0
            }
            self.annotations.append(annotation)
            self.coco_data["annotations"].append(annotation)
            self.annotation_id = self.get_next_annotation_id()
            self.bboxes.append([x, y, width, height])
            
            # Update the image with the new bounding box
            self.display_image_with_boxes()
        # else:
            # Remove the rectangle if it's invalid
        self.canvas.delete(self.rect)
        self.rect = None

    def save_annotations(self):
        # Save the annotations to the JSON file
        with open(self.json_path, 'w') as f:
            json.dump(self.coco_data, f, indent=4)
        messagebox.showinfo("Annotations Saved", f"Annotations saved to {self.json_path}")

    def scale_up(self):
        """Increase the scale factor and redraw the image."""
        self.scale_factor += 0.1
        self.update_image()

    def scale_down(self):
        """Decrease the scale factor and redraw the image."""
        # Prevent scale_factor from going too low
        if self.scale_factor > 0.2:
            self.scale_factor -= 0.1
        self.update_image()

    def update_image(self):
        """Resize the image according to the current scale_factor and update canvas."""
        # Compute new dimensions based on the original image
        self.drawn_image = self.image.copy()
        new_width = int(self.drawn_image.width * self.scale_factor)
        new_height = int(self.drawn_image.height * self.scale_factor)

        # Resize using Pillow (LANCZOS gives good quality)
        self.drawn_image = self.drawn_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to Tkinter image
        self.tk_image = ImageTk.PhotoImage(self.drawn_image)

        # Update the existing canvas image object
        self.canvas.itemconfig(self.image_container, image=self.tk_image)

        # Update scroll region to match the new size
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.set_screen_size_dynamically()
        self.display_image_with_boxes()


if __name__ == "__main__":
    root = tk.Tk()
    app = BoundingBoxEditor(root)
    root.mainloop()

