import rasterio as rio
import numpy as np
from PIL import Image


def lets_check(image_file_name, req_num_bands):
    raster = image_file_name            # The name and/or path of the image file
    src = rio.open(raster)
    if check_bands(src, req_num_bands):     # If function 'check_bands' returns a boolean of True, return same
        return True
    elif change_num_image_bands(src, "Test1a.png", req_num_bands):      # If 'check_bands' returns False, then call function 'change_num_image_bands' to fix it
        return True                                                                                                           # If that is successful and returns a boolean of True, return same
    else:                                                                                                                           # Otherwise return a boolean of False
        return False


def change_num_image_bands(img_raster, img_f_name, req_number):
    numpy_image = img_raster.read()
    numpy_image = np.moveaxis(numpy_image, 0, 2)
    numpy_image = numpy_image[:, :, :req_number].astype("uint8")
    image = Image.fromarray(numpy_image)
    image.save(img_f_name)
    # TODO: When can I check the number of bands again? Can I check before I save the image from an array?
    #              Also need to have a return statement


def check_bands(source, req_num):
    if source.read().shape[0] == req_num:           # If the image has the desired number of bands, return True
        return True
    else:                                                                   # Otherwise, return False
        return False


