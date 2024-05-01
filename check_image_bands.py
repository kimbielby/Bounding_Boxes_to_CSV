import rasterio as rio
import numpy as np
from PIL import Image

"""
Handles all functions
Params
    image_file_name: The name (and path) of the image to check
    req_num_bands: The number of bands in the image that we want 
Returns a boolean: True if the image has the correct number of bands, otherwise False 
"""
def lets_check(image_file_name, req_num_bands):
    try:
        raster = image_file_name
        src = rio.open(raster)
        if check_bands(src, req_num_bands):
            return True
        elif change_num_image_bands(src, image_file_name, req_num_bands):      # If 'check_bands' returns False, then call function 'change_num_image_bands' to fix it
            return True                                                                                                                    # If that is successful and returns a boolean of True, return same
        else:
            return False
    except RuntimeError as e:
        print(e)

"""
Changes the number of bands in the image to the correct amount and saves updated image.
Calls function lets_check to make sure it worked. 
Params
    img_raster: The image already opened by rasterio 
    img_f_name: The name (and path) of the image
    req_number: The number of bands we want the image to have 
Returns True if change was successful 
"""
def change_num_image_bands(img_raster, img_f_name, req_number):
    try:
        numpy_image = img_raster.read()
        numpy_image = np.moveaxis(numpy_image, 0, 2)
        numpy_image = numpy_image[:, :, :req_number].astype("uint8")
        image = Image.fromarray(numpy_image)
        image.save(img_f_name)
        return check_bands(img_raster, req_number)
    except RuntimeError as e:
        print(e)
        return False

"""
Checks that the image has the correct number of bands.
Params
    source: Image to check, already opened by rasterio
    req_num: The number of bands we want the image to have
Returns True if image already has correct number of bands, otherwise False. 
"""
def check_bands(source, req_num):
    try:
        if source.read().shape[0] == req_num:
            return True
        else:
            return False
    except RuntimeError as e:
        print(e)
