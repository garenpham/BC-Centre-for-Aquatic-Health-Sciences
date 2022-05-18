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
        