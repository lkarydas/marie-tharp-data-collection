from PIL import Image
import os
from tqdm import tqdm
from datetime import datetime
import cv2
import numpy as np

def detect_and_match_keypoints(img1, img2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

    # Use ORB (Oriented FAST and Rotated BRIEF) to detect keypoints and compute descriptors
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    # Use the Brute-Force matcher to find the best matches between descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort the matches based on their distances
    matches = sorted(matches, key=lambda x: x.distance)

    # Get the keypoints for the best matches
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Use RANSAC to estimate the transformation matrix
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    return M

def blend_images(img1, img2, transformation_matrix):
    # Warp the second image to align with the first image
    h, w = img1.shape[:2]
    result = cv2.warpPerspective(img2, transformation_matrix, (w, h))

    # Blend the images using alpha blending
    blended = cv2.addWeighted(img1, 0.5, result, 0.5, 0)

    return blended

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
                images_row.append(np.array(Image.open(image_path)))
        else:
            for i in range(start_index, end_index):
                image_path = os.path.join(images_folder, f"_{i}.jpg")
                images_row.append(np.array(Image.open(image_path)))

        # Get the dimensions of a single image
        height, width, _ = images_row[0].shape

        # Create a new blank image with the width to accommodate the images horizontally
        result = images_row[0].copy()

        # Iterate through images to align and blend
        for i in range(1, images_per_row):
            transformation_matrix = detect_and_match_keypoints(result, images_row[i])
            result = blend_images(result, images_row[i], transformation_matrix)

        # Convert the result back to PIL Image
        result_pil = Image.fromarray(result)

        # Save the stitched row image
        output_path = os.path.join(output_folder, f"stitched_row_{row}.jpg")
        result_pil.save(output_path)

        # Add the path of the stitched row to the list
        stitched_rows_paths.append(output_path)

    # Stitch all row images together vertically
    final_result = Image.new('RGB', (width * images_per_row, height * total_rows))
    for i, row_path in enumerate(stitched_rows_paths):
        row_image = Image.open(row_path)
        final_result.paste(row_image, (0, i * height))

    # Save the final stitched image
    while True:
        user_input = input("Enter a name for the stitched image (press Enter for default name): ").strip()
        if not user_input:
            user_input = f"stitched_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        final_output_path = os.path.join(output_folder, user_input)
        if not os.path.exists(final_output_path):
            break
        else:
            print("A file with the same name already exists. Please choose a different name.")

    final_result.save(final_output_path)
    print(f"\nFinal stitched image saved at {final_output_path}")

if __name__ == "__main__":
    # Replace 'images_folder' with the path to the folder containing your images
    images_folder = "/path/to/your/images"
    # Replace 'output_folder' with the path to the folder where you want to save the stitched images
    output_folder = "/path/to/your/output/folder"

    stitch_images(images_folder, output_folder)