"""
Module for miscellaneous functions.
"""


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
    return {
        key: None
        if value == '' or (key == 'sample-type' and value == 'All')
        else value
        for key, value in form_data.items()
        }
