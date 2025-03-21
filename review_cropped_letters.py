import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import argparse

# Directory containing the images
def main(letters_annotations_dir, script_mode, category_id,output_dir):
    if letters_annotations_dir is None:
        letters_annotations_dir = r"cropped_annotations"
        image_dir = os.path.join(letters_annotations_dir, script_mode, str(category_id))
        name = image_dir.replace("cropped_annotations\\","").replace('\\','_')
    else:
        name = letters_annotations_dir
        image_dir = letters_annotations_dir
    if output_dir is None:
        output_file =f"wrong-image-classes_{name}.txt"
    else:
        output_file = os.path.join(output_dir, f"wrong-image-classes_{name}.txt")
                


    # Get a list of all image files in the directory
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Dictionary to store the real class of each image
    image_classes = {}

    # Initialize the Tkinter GUI
    root = tk.Tk()
    root.title("Image Reviwer")
    sub_title = tk.Label(root, font=("Arial", 12),
     text=f"Review the cropped images of category_id {category_id} in script_mode {script_mode}, and enter the correct class for each image ONLY if the class is wrong. The results will be saved to '{output_file}'.")
    sub_title.pack()
    # Set up the display
    
    global current_index
    current_index = 0
    images_per_page = 15

    # Function to load and display the current set of images
    def show_images():
        global current_index, image_labels, class_entries
        image_labels = []
        class_entries = []

        # Clear the previous images and entries
        for widget in image_frame.winfo_children():
            widget.destroy()

        # Display 15 images at a time
        for i in range(images_per_page):
            if current_index + i < len(image_files):
                img_path = os.path.join(image_dir, image_files[current_index + i])
                img = Image.open(img_path)
                img.thumbnail((150, 150))  # Resize image to fit the grid
                img_tk = ImageTk.PhotoImage(img)

                # Create a label for the image
                img_label = tk.Label(image_frame, image=img_tk)
                img_label.image = img_tk  # Keep a reference to avoid garbage collection
                img_label.grid(row=i // 5, column=(i % 5) * 2, padx=10, pady=10)
                image_labels.append(img_label)

                # Create an entry for the class
                class_entry = tk.Entry(image_frame, width=20)
                class_entry.grid(row=i // 5, column=(i % 5) * 2 + 1, padx=10, pady=10)
                class_entries.append(class_entry)
            else:
                break

        status_label.config(text=f"Images {current_index + 1} to {min(current_index + images_per_page, len(image_files))} of {len(image_files)}")

    # Function to save the classes for the current set of images
    def save_classes():
        global current_index
        for i in range(images_per_page):
            if current_index + i < len(image_files):
                class_name = class_entries[i].get()
                if class_name:
                    image_classes[image_files[current_index + i]] = class_name
        next_page()

    # Function to move to the next set of images
    def next_page():
        global current_index
        current_index += images_per_page
        if current_index < len(image_files):
            show_images()
        else:
            messagebox.showinfo("End", "You have reviewed all images.")
            save_results()
            root.destroy()

    # Function to save the results to a file
    def save_results():
        with open(output_file, "w") as f:
            for img, cls in image_classes.items():
                f.write(f"{img}: {cls}\n")
        messagebox.showinfo("Saved", f"The image classes have been saved to '{output_file}'.")

    # Frame to hold the images and class entries
    image_frame = tk.Frame(root)
    image_frame.pack()

    # Buttons for user interaction
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    save_button = tk.Button(button_frame, text="Save and Next", command=save_classes)
    save_button.pack(side=tk.LEFT, padx=10)

    # Status label to show current image range
    status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X)

    # Start by showing the first set of images
    show_images()

    # Run the Tkinter event loop
    root.mainloop()

    # Print the image classes after the GUI closes
    print("Image classes:", image_classes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review cropped letters.")
    parser.add_argument("--letters_annotations_dir", required=False, help="Directory containing the cropped letters.", )
    parser.add_argument("--script_mode", required=True, help="Script mode (e.g., 'german').")
    parser.add_argument("--category_id", type=int, required=True, help="Category ID (e.g., 1).")
    parser.add_argument("--output_dir", required=False, help="Output dir to save the results.")
    args = parser.parse_args()
    
    main(args.letters_annotations_dir, args.script_mode, args.category_id, args.output_dir)