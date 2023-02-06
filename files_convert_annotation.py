from logging import exception
import os
import os.path
import cv2
import numpy as np
from tqdm import tqdm
import argparse
import fileinput
import shutil
import re

YOLO_ORGANIZE = False


# function that turns XMin, YMin, XMax, YMax coordinates to normalized yolo format
def convert(filename_str, coords):
    os.chdir("..")
    load_path = os.path.join(os.getcwd(), filename_str)
    image = cv2.imread(load_path + ".jpg")
    coords[2] -= coords[0]
    coords[3] -= coords[1]
    x_diff = int(coords[2] / 2)
    y_diff = int(coords[3] / 2)
    coords[0] = coords[0] + x_diff
    coords[1] = coords[1] + y_diff
    coords[0] /= int(image.shape[1])
    coords[1] /= int(image.shape[0])
    coords[2] /= int(image.shape[1])
    coords[3] /= int(image.shape[0])
    os.chdir("Label")
    return coords


ROOT_DIR = os.getcwd()

# create dict to map class names to numbers for yolo
classes = {}
with open("classes.txt", "r") as myFile:
    for num, line in enumerate(myFile, 0):
        line = line.rstrip("\n")
        classes[line] = num
    myFile.close()
# step into dataset directory
os.chdir(os.path.join("OID", "Dataset"))
DIRS = os.listdir(os.getcwd())

# for all train, validation and test folders
for DIR in DIRS:
    if os.path.isdir(DIR):
        os.chdir(DIR)
        print("Currently in subdirectory:", DIR)

        CLASS_DIRS = os.listdir(os.getcwd())
        # for all class folders step into directory to change annotations
        for CLASS_DIR in CLASS_DIRS:
            if os.path.isdir(CLASS_DIR):
                os.chdir(CLASS_DIR)
                print("Converting annotations for class: ", CLASS_DIR)
                if not os.path.exists("Label_yolo"):
                    os.makedirs("Label_yolo")
                if not os.path.exists("class_names.txt"):
                    raise Exception(
                        "Missing 'class_names.txt' this is needed to convert classes"
                    )

                list_of_class_names = []
                with open("class_names.txt") as f:
                    list_of_class_names = [class_name.strip() for class_name in f]

                print("\n\n\n\n", list_of_class_names)
                # Step into Label folder where annotations are generated
                os.chdir("Label")
                for filename in tqdm(os.listdir(os.getcwd())):
                    filename_str = str.split(filename, ".")[0]
                    if filename.endswith(".txt"):
                        annotations = []
                        with open(filename) as f:
                            for line in f:
                                for given_classes in list_of_class_names:
                                    try:
                                        line = line.replace(
                                            given_classes,
                                            given_classes.lower().replace(" ", "_"),
                                        )  ### Some classes have 2 names
                                        line = line.replace(
                                            given_classes[0].upper()
                                            + given_classes[1:].replace("_", " "),
                                            given_classes.lower().replace(" ", "_"),
                                        )
                                    except:
                                        pass

                                for class_type in classes:
                                    # print(class_type)
                                    line = re.sub(
                                        rf"\b{class_type}\b",
                                        str(classes.get(class_type)),
                                        line,
                                    )  ### Regex to handle spaces
                                    # line = line.replace(class_type, str(classes.get(class_type)))
                                labels = line.split()
                                coords = np.asarray(
                                    [
                                        float(labels[1]),
                                        float(labels[2]),
                                        float(labels[3]),
                                        float(labels[4]),
                                    ]
                                )
                                coords = convert(filename_str, coords)
                                labels[1], labels[2], labels[3], labels[4] = (
                                    coords[0],
                                    coords[1],
                                    coords[2],
                                    coords[3],
                                )
                                newline = (
                                    str(labels[0])
                                    + " "
                                    + str(labels[1])
                                    + " "
                                    + str(labels[2])
                                    + " "
                                    + str(labels[3])
                                    + " "
                                    + str(labels[4])
                                )
                                line = line.replace(line, newline)

                                annotations.append(line)

                            f.close()
                        os.chdir("..")
                        os.chdir("Label_yolo")
                        with open(filename, "w") as outfile:
                            for line in annotations:
                                outfile.write(line)
                                outfile.write("\n")
                            outfile.close()
                        os.chdir("..")
                        os.chdir("Label")
            os.chdir("..")
            os.chdir("..")

            # To organize all the image in the folder to a new folder ( breaks the code as it cannot be run again )
            if YOLO_ORGANIZE == True:
                if os.path.isdir(CLASS_DIR):
                    os.chdir(CLASS_DIR)

                    if not os.path.exists("Images"):
                        os.makedirs("Images")

                    for filename in tqdm(os.listdir(os.getcwd())):
                        # print("Moving Images for Class: ", CLASS_DIR)
                        filename_str = str.split(filename, ".")[0]
                        if filename.endswith(".jpg"):
                            src_path = str(os.getcwd()) + "\\" + filename
                            print(src_path)
                            os.chdir("Images")
                            dst_path = str(os.getcwd()) + "\\" + filename
                            print(dst_path)
                            shutil.move(src_path, dst_path)
                            os.chdir("..")
                os.chdir("..")
        os.chdir("..")
