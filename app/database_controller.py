"""
Defines common logic for database access.
"""

import os
import sys
import mysql.connector


def mysql_database_connection():
    """
    Establishes a connection to the MySQL database.
    """

    try:
        database = mysql.connector.connect(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            user=os.environ['DB_USER'],
            passwd=os.environ['DB_PASS'],
            auth_plugin=os.environ['DB_AUTH_PLUGIN'],
            database=os.environ['DB'],
        )
    except mysql.connector.Error as err:
        print(f"error connecting to the database. please verify that MySQL is running.{err}")
        sys.exit()

    return database
