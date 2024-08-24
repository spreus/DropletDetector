import os
from datetime import datetime

from Functions.files import select_image_directory, get_first_image_filepath, write_to_excel, \
    open_excel_file
from Functions.image_processing import select_roi, process_images_in_directory

if __name__ == '__main__':
    image_directory = select_image_directory("Select Image Directory")
    if image_directory:
        # Output dir
        output_directory = image_directory + "/" + datetime.now().strftime("%Y%m%d_%H%M%S")
        os.mkdir(output_directory)

        # Select ROI
        roi = select_roi(get_first_image_filepath(image_directory))

        # Find droplets
        droplets = process_images_in_directory(image_directory, roi, output_directory)

        # Write results to file
        output_excel_file = output_directory + "/result.xlsx"
        write_to_excel(droplets, output_excel_file)

        # Open generated file
        open_excel_file(output_excel_file)
