from PIL import Image, ImageOps
import os
from tqdm import tqdm
from datetime import datetime

invert = True


def stitch_images(images_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Calculate the number of rows needed
    total_images = 320
    images_per_row = 16
    total_rows = total_images // images_per_row

    # List to store the paths of the stitched rows
    stitched_rows_paths = []

    # Iterate through each row
    for row in tqdm(range(total_rows), desc="Stitching Progress", unit="row"):
        start_index = row * images_per_row
        end_index = start_index + images_per_row

        # Create a list to store images for the current row
        images_row = []

        # Iterate through images in reverse order for the first row, then forward for the next, and so on
        if row % 2 == 0:
            for i in range(end_index - 1, start_index - 1, -1):
                image_path = os.path.join(images_folder, f"_{i}.jpg")
                images_row.append(Image.open(image_path))
        else:
            for i in range(start_index, end_index):
                image_path = os.path.join(images_folder, f"_{i}.jpg")
                images_row.append(Image.open(image_path))

        # Get the dimensions of a single image
        width, height = images_row[0].size

        # Create a new blank image with the width to accommodate the images horizontally
        result = Image.new('RGB', (width * images_per_row, height))

        # Paste each image into the result image at the corresponding position
        for i in range(images_per_row):
            result.paste(images_row[i], (i * width, 0))

        # Save the stitched row image
        output_path = os.path.join(output_folder, f"stitched_row_{row}.jpg")
        result.save(output_path)

        # Add the path of the stitched row to the list
        stitched_rows_paths.append(output_path)

    # Stitch all row images together vertically
    final_result = Image.new('RGB', (width * images_per_row, height * total_rows))
    for i, row_path in enumerate(stitched_rows_paths):
        row_image = Image.open(row_path)
        final_result.paste(row_image, (0, i * height))

    # Save the final stitched image
    while True:
        user_input = input("Enter a name for the stitched image without extension (or press Enter for default name): ").strip()
        if not user_input:
            user_input = f"stitched_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        final_output_path = os.path.join(output_folder, user_input + ".jpg")
        
        if not os.path.exists(final_output_path):
            break
        else:
            print("A file with the same name already exists. Please choose a different name.")

    final_result.save(final_output_path)
    print(f"\nFinal stitched image saved at {final_output_path}")
    
    
    if invert:
        # Invert the colors of the final stitched image
        final_result = ImageOps.invert(final_result)
        final_output_path = final_output_path.replace(".jpg","_inv.jpg")
        final_result.save(final_output_path)
        print(f"Final stitched iverted image saved at {final_output_path}")

if __name__ == "__main__":
    # Replace 'images_folder' with the path to the folder containing your images
    images_folder = "/home/pi/Downloads/EnderScope-main/Software/Img/"
    # Replace 'output_folder' with the path to the folder where you want to save the stitched images
    output_folder = "/home/pi/Downloads/EnderScope-main/Software/Stitched_OUT/"

    stitch_images(images_folder, output_folder)