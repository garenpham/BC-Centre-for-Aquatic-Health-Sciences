"""
Module for miscellaneous functions.
"""
import os
from werkzeug.datastructures import MultiDict

def generate_csv(results, headers):
    """
    Generator for creating .csv file for master sample view
    """
    for i, header in enumerate(headers):
        yield str(header)
        if i < len(headers) - 1:
            yield ','
    yield "\n"
    for result in results:
        for j, item in enumerate(result):
            if ',' in str(item):
                yield f'"{item}"'
            else:
                yield str(item)
            if j < len(result) - 1:
                yield ','
        yield "\n"

def create_species_list():
    species = []
    with open("./app/static/samples/species.csv", 'r', encoding='utf-8') as species_file:
        for line in species_file:
            line = line.replace('"', '')
            line = line.replace("\n", '')
            species.append(line)
    return species

def sanitize_form_data(form_data):
    """
    Replaces empty strings with None.
    """
    return {key: None if value == '' else value for key, value in form_data.items()}


def sanitize_abund_form_data(form_data):
    """
    Replaces empty strings and 'All' sample type with None in
    form data for abundance graph filters.
    """
    return sanitize_trend_form_data(form_data)
    return {
        key: None
        if value == '' or (key == 'sample-type' and value == 'All')
        else value
        for key, value in form_data.items()
        }


def sanitize_trend_form_data(form_data):
    """
    Replaces empty strings and 'All' sample type with None in
    form data for abundance graph filters.
    """
    # Delcare return array
    return_dict = {}
    for key, value in form_data.items():
        # Iterate through items
        # NOTE: form_data.items() returns only 1 VALUE for EACH key (duplicate key value pairs are ignored!)
        if key == '':
            continue
        if (key == 'sample-type' and value == 'ALL'):
            return_dict[key] = None
        elif key != 'sample-type':
            return_dict[key] = value
        else:
            return_dict[key] = value
    # MultiDict.getlist('key') returns all values for a given key in multi dict.
    if len(form_data.getlist('species-select')) > 1:
        # If there is more than one species selected, append all values to list
        return_dict['species-select'] = form_data.getlist('species-select')
        
    return return_dict
