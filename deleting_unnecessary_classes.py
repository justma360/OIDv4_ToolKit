from cProfile import label
from logging import exception
import os
import os.path
import cv2
from matplotlib.font_manager import list_fonts
import numpy as np
from tqdm import tqdm
import argparse
import fileinput
import shutil
import re

ROOT_DIR = os.getcwd()

directory_to_modify = os.path.join(
    ROOT_DIR, "OID", "Dataset", "train", "bicycle_helmet_bicycle_person", "Label"
)
images_dir_to_modify = os.path.join(
    ROOT_DIR, "OID", "Dataset", "train", "bicycle_helmet_bicycle_person"
)

list_of_labels = os.listdir(directory_to_modify)

# Only labels / images that contain the below
common_class_to_keep = ["Bicycle helmet"]
images_to_keep = []


def find_common_class_files():
    list_of_labels = os.listdir(directory_to_modify)
    for file_name in list_of_labels:
        # print(file_name)
        file_path_name = os.path.join(directory_to_modify, file_name)
        f = open(file_path_name, "r")
        label_lines = f.readlines()
        txt_data = "".join(label_lines)
        for keep_classes in common_class_to_keep:
            if keep_classes in txt_data:
                images_to_keep.append(file_name)
                break
        f.close()
        # print()

    print(f"Number of image that will be kept: {len(images_to_keep)}")
    print(
        f"Ratio of images that are being kept {len(images_to_keep)/len(list_of_labels)}"
    )


def delete_unrelated():
    print("DELETING...")
    for file_name in list_of_labels:
        if file_name not in images_to_keep:
            pre, ext = os.path.splitext(file_name)
            image_name = pre + ".jpg"
            file_path_name = os.path.join(directory_to_modify, file_name)
            image_path_name = os.path.join(images_dir_to_modify, image_name)
            yolo_label_path_name = os.path.join(
                images_dir_to_modify, "Label_yolo", file_name
            )

            print(image_path_name)
            print(file_path_name)
            print(yolo_label_path_name)

            os.remove(file_path_name)
            os.remove(image_path_name)
            try:
                os.remove(yolo_label_path_name)
            except:
                pass

    print("\nFinished deleting unused images and labels")


if __name__ == "__main__":
    find_common_class_files()
    delete = input(
        f"\n\tWould you like to delete the unrelated images? (keeping only labels + images of {common_class_to_keep}) | Enter (Y)es/(N)o : "
    )
    print()

    if delete.lower() == "y":
        print(f"Deleting images and labels")
        delete_unrelated()
    else:
        print(f"You have selected to not delete the images and labels")
