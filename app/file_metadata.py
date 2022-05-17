"""
Defines logic for reading and writing file metadata.
For now, file metadata is a JSON file adjacent to any given data file with a title and description.
"""

import os
import json


def locate_file_metadata(file_path):
    """
    Locates the JSON metadata file pertaining to the file at the given path.
    :param file_path: a string denoting the path of the file whose metadata to locate
    :return: a string
    """
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_base, _ = os.path.splitext(file_name)
    meta_name = f"{file_base}.json"
    return os.path.join(dir_path, meta_name)


def read_file_metadata(file_path):
    """
    Reads in file JSON metadata pertaining to the file at the given path.
    :param file_path: a string denoting the path of the file whose metadata to read from
    :return: a (file_name, file_title, file_description) tuple
    """

    if not os.path.isfile(file_path):
        return None

    # exception for JSON files: used as metadata storage for file title and description
    # the JSON files themselves shouldn't be displayed in the app
    if file_path.endswith(".json"):
        return None

    file_name = os.path.basename(file_path)
    file_base, _ = os.path.splitext(file_name)
    meta_path = locate_file_metadata(file_path)

    try:
        with open(meta_path, mode="r", encoding="utf-8") as meta_file:
            meta_buffer = meta_file.read()
        meta_data = json.loads(meta_buffer)
    except FileNotFoundError:
        meta_data = {
            "title": file_base,
            "description": "",
        }

    file_title = meta_data["title"]
    file_description = meta_data["description"]
    return (file_name, file_title, file_description)


def write_file_metadata(file_path, title, description):
    """
    Writes the given data to the JSON metadata file pertaining to the file at the given path.
    :param file_path: a string denoting the path of the file whose metadata to update
    :param title: a string denoting the file title
    :param description: a string denoting the file description
    """

    meta_buffer = json.dumps({
        "title": title,
        "description": description,
    }, separators=(",", ":"))

    meta_path = locate_file_metadata(file_path)
    with open(meta_path, mode="w", encoding="utf-8") as meta_file:
        meta_file.write(meta_buffer)
