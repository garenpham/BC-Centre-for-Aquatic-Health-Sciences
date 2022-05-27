"""
Defines constants in a centralized manner.
"""

# Only allows queries with valid FROM clauses
VIEWS_WHITELIST = [
    "hatchery_data_view",
    "sample_data_view",
    "master_sample_data_view",
    "environmental_data_view"
    ]

START_OF_TIME = "0000-01-01"

END_OF_TIME = "9999-12-31"
