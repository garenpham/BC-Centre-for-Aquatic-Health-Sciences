import mysql.connector
import pandas as pd
import os


def mysql_database_connection():
    """MySQL Database Connection"""
    try:
        db = mysql.connector.connect(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            user=os.environ['DB_USER'],
            passwd=os.environ['DB_PASS'],
            auth_plugin=os.environ['DB_AUTH_PLUGIN'],
            database=os.environ['DB'],
        )
    except mysql.connector.Error as err:
        print(f"error connecting to the database. please verify that MySQL is running.{err}")
        exit()
    return db


def show_location_data():
    """Shows location data by using a SELECT statement"""
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        headers = []
        cursor.execute("SELECT * FROM location ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM location ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print("Something went wrong pulling location data from database: {}".format(err))


def show_sample_info():
    """Shows sample info by using a SELECT statement"""
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        headers = []
        cursor.execute("SELECT * FROM sample_data_view ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM sample_data_view ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print("Something went wrong pulling sample info from database: {}".format(err))


def show_submission_data():
    """Show Submission data by using a SELECT statement"""
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        headers = []
        cursor.execute("SELECT * FROM submission_data ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM submission_data ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print("Something went wrong pulling submission data from database: {}".format(err))


def show_sample_data():
    """Show sample data by using the SELECT statement"""
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        headers = []
        cursor.execute("SELECT * FROM sample_info ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM sample_info ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print("Something went wrong pulling location data from database: {}".format(err))
