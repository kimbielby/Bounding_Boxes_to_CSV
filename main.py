import copy
import os.path
import numpy as np
import json
import rasterio as rio
import pandas as pd

""" Global Variables """
img_left_bounds = 0              # Left boundary of image in geo-coordinates
img_right_bounds = 0            # Right boundary of image in geo-coordinates
img_top_bounds = 0              # Top boundary of image in geo-coordinates
img_bottom_bounds = 0       # Bottom boundary of image in geo-coordinates
img_width_px = 0                 # Width of image in pixels
img_height_px = 0                # Height of image in pixels
px_per_m = 0                       # Number of pixels per metre of geo-coordinates

def here_we_go(geojson_filepath, img_filepath, new_csv_name, label):
    """
    Handles all functions
    :param geojson_filepath: The name (and path) of the geojson file
    :param img_filepath: The name (and path) of the image
    :param new_csv_name: The name (and path to) of the new csv file to be created
    :param label: What you want to label the feature (e.g. 'tree' or 'oak')
    """
    poss_id, tree_annot = get_valid_id(geojson_filepath, img_filepath)
    full_coords_list = get_id_coords(poss_id, tree_annot)
    list_for_csv = making_lists_for_csv(img_filepath, full_coords_list, label)
    create_csv(list_for_csv, new_csv_name)

def get_valid_id(geo_json_file, img_filepath):
    """
    Gets a list of id's from the geojson file whose bounding boxes geo-
    coordinates are within those of the image
    :param geo_json_file: The name (and path) of the geojson file
    :param img_filepath: The name (and path) of the image to check
    :return: List of possible id's from the geojson file and the loaded
        geojson file
    """
    # Open the GeoJSON file and load it with JSON
    geo_j_file = open(geo_json_file)
    tree_annotations = json.load(geo_j_file)

    # Empty list to put in id numbers of possible bounding boxes in image
    poss_id_list = []

    # Calculate image coordinates
    calc_px_per(img_filepath)

    # Check the first x-y coordinate of each id to see if it is within bounds
    for i in tree_annotations["features"]:  # Check each bounding box
        id_num = i["properties"]["fcode"]

        # Hold all the arrays of each vertex in the current bounding box
        coords_array = np.array(i["geometry"]["coordinates"])

        if len(coords_array) > 0:  # Make sure the coordinates arrays are not empty
            current_bbox = coords_array[0][0]  # First vertex of the current bounding box for geojson file

            # Make sure that the x and y coordinates of the first vertex are within image bounds
            if img_right_bounds >= current_bbox[0] >= img_left_bounds and img_top_bounds >= current_bbox[1] >= \
                    img_bottom_bounds:
                poss_id_list.append(id_num)  # Append id to list if first coordinates are within bounds

    return poss_id_list, tree_annotations

def calc_px_per(img_file):
    """
    Calculates the width and height of the image, in both pixels and geo-
    coordinates, as well as pixels per metre.
    Updates global vars.
    :param img_file: The image file
    """
    global img_width_px
    global img_height_px
    global px_per_m

    # Update the global variables with the Geolocation boundaries of image
    calc_geo_coords_boundaries(img_file)

    # Load the image
    the_image = rio.open(img_file)

    # Width and Height of image in pixels
    img_width_px = the_image.width
    img_height_px = the_image.height

    # Width of image in geo-coordinate metres
    x_coords_span = img_right_bounds - img_left_bounds

    # Image pixels per geo-coordinate metre
    px_per_m = img_width_px / x_coords_span

def calc_geo_coords_boundaries(img_file):
    """
    Calculates the geo-location boundaries of the image & updates global
    variables
    :param img_file: The image file
    """
    global img_left_bounds
    global img_right_bounds
    global img_top_bounds
    global img_bottom_bounds

    # Open and read the image file
    the_image = rio.open(img_file)

    # Calculate the geolocation boundaries of the image (& update global variables)
    img_left_bounds = the_image.bounds.left
    img_right_bounds = the_image.bounds.right
    img_top_bounds = the_image.bounds.top
    img_bottom_bounds = the_image.bounds.bottom

def get_id_coords(id_list, annot_file):
    """
    Gets geo-coordinates for each id on id_list and stores them in a 2D
    List
    :param id_list: The list of possible id's from the geojson file
    :param annot_file: The loaded geojson file
    :return: List of geo-coordinates for all id's
    """
    # Go through geojson and get coordinates for each id in id_list
    full_coords_list = []

    for i in id_list:
        for j in annot_file["features"]:
            if i == j["properties"]["fcode"]:
                full_coords_list.append(j["geometry"]["coordinates"])

    return full_coords_list

def making_lists_for_csv(img_name, coord_list, label):
    """
    Gets the min and max geo-locations of bounding box height and width
    then converts to pixels
    :param img_name: The image file name
    :param coord_list: The List of coordinates for the image
    :param label: The label given to that bounding box
    :return: The multi-dimensional List with image name, bounding box
        details in pixels and label
    """
    # Take certain coordinates from full_coords_list and put them into a separate list with the following pattern:
    # image_path (name of image); xmin; ymin; xmax; ymax; label (e.g. 'Tree')

    # Create empty list
    for_csv_list = []

    for i in coord_list:
        # Get mins and maxs of bounding box
        geo_xmin = i[0][0][0]
        geo_ymin = i[0][0][1]
        geo_xmax = i[0][2][0]
        geo_ymax = i[0][1][1]

        # Put all vars in the necessary order for a line in csv
        temp_list = [img_name, geo_xmin, geo_ymin, geo_xmax, geo_ymax, label]

        # Add that bounding box list to the list of all bounding boxes in image
        for_csv_list.append(temp_list)

    # Return copy of for_csv_list but with the image's pixel min-max for each bounding box instead of the geo versions
    return calc_img_px_coords(for_csv_list)

def calc_img_px_coords(list_for_csv):
    """
    Calculates the image's pixel min-max for each bounding box and
    replaces their geo-coordinate equivalent in for_csv_list
    :param list_for_csv: List that holds image name, mins and maxes and
        label
    :return: list_for_csv with updated mins and maxes
    """
    list_for_csv_copy = copy.deepcopy(list_for_csv)
    # Calculate image pixel min-max for bounding box and replace their geo-coordinate equivalent in for_csv List
    for i in range(len(list_for_csv_copy)):
        # The xmin in pixels: geo-coordinates of left edge of bounding box minus geo-coordinates of left edge of image
        # Multiplied by pixels per metre to turn geo-coordinate difference into pixel difference

        # REMEMBER: image pixel coordinates start top-left, NOT bottom-left
        px_xmin = (list_for_csv_copy[i][1] - img_left_bounds) * px_per_m
        px_ymin = (img_top_bounds - list_for_csv_copy[i][4]) * px_per_m
        px_xmax = (img_right_bounds - list_for_csv_copy[i][3]) * px_per_m
        px_ymax = (img_top_bounds - list_for_csv_copy[i][2]) * px_per_m

        if px_xmin < 0:     # If the left edge of bounding box is past the left edge of the image
            px_xmin = 0     # Set the xmin value to the left edge of the image (i.e. 0)
        if px_ymin < 0:     # If the top edge of bounding box is above the top edge of the image
            px_ymin = 0     # Set the ymin to the top edge of the image (i.e. 0)
        if px_xmax > img_width_px:      # If the right edge of the bounding box is past the right edge of the image
            px_xmax = img_width_px      # Set the xmax to the width of the image
        if px_ymax > img_height_px:     # If the bottom edge of the bounding box is below the bottom edge of the image
            px_ymax = img_height_px     # Set the ymax to the height of the image

        # Replace items in positions 1 through 4 in the List
        list_for_csv_copy[i][1:5] = [px_xmin, px_ymin, px_xmax, px_ymax]

    return list_for_csv_copy

def create_csv(list_for_csv, csv_name):
    """
    Adds column headers and data to a Pandas dataframe then saves it
    as a csv file
    :param list_for_csv: List with image name, mins and maxes, and label
    :param csv_name: What the csv will be called, including path
    """
    # Column headers to be in csv file
    columns = ["image_path", "xmin", "ymin", "xmax", "ymax", "label"]

    # Check if csv file already exists
    if os.path.exists(csv_name):    # If exists...
        temp_df1 = pd.read_csv(csv_name)     # Read csv into Pandas dataframe - including column headers
        temp_df2 = pd.DataFrame(list_for_csv, columns=columns)  # Create Pandas dataframe with new data plus headers
        main_df = temp_df1.merge(temp_df2, how="outer")    # Create new dataframe with rows of second dataframe below those in first dataframe
        main_df.to_csv(csv_name, index=False)  # Create csv from new dataframe with column headers and no extra index column
    else:   # If does not exist...
        main_df = pd.DataFrame(list_for_csv, columns=columns)  # Create pandas dataframe
        main_df.to_csv(csv_name, index=False)    # Create csv with column headers and no extra index column


