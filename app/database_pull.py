"""
Defines logic for pulling from the database.
"""
import datetime

import mysql.connector
from .database_controller import initialize_database_cursor


def get_hatcheries():
    """
    Gets a dict {id: name} of available hatcheries
    """
    _, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT * FROM location ;")
        result = cursor.fetchall()
        return dict(result)
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling location data from database: {err}")
        return {}


def get_sample_by_sample_id(sample_id):
    """
    Gets sample data by sample ID
    """

    _, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT * FROM sample_info WHERE `Sample ID` LIKE %(sample_id)s;",
                       {"sample_id": sample_id})
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling sample data from database: {err}")
        return []


def get_submission_by_submission_no(submission_no):
    """
    Gets environmental data by CAHS submission number
    """

    _, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT * FROM submission_data"
                       " WHERE `CAHS Submission Number` LIKE %(submission_no)s;",
                       {"submission_no": submission_no})
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling environmental data from database: {err}")
        return [], []


def show_hatchery_data():
    """Shows location data by using a SELECT statement"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        cursor.execute("SELECT * FROM hatchery_data_view ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM hatchery_data_view ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling location data from database: {err}")
        return [], []


def show_environmental_data():
    """Show environmental data by using a SELECT statement"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        cursor.execute("SELECT * FROM environmental_data_view ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM environmental_data_view ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling submission data from database: {err}")
        return [], []


def show_sample_data():
    """Show sample data by using the SELECT statement"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        cursor.execute("SELECT * FROM sample_data_view ;")
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM sample_data_view ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        result_list = [[str(item) if isinstance(item, datetime.timedelta)
                        else item for item in entry]
                       for entry in result]
        return result_list, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling location data from database: {err}")
        return [], []


def get_all_sample_data(sample_id=None):
    """Queries for all sample data, can be by sample ID"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        if sample_id is None:
            cursor.execute("SELECT * FROM master_sample_data_view ;")
            result = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT * FROM master_sample_data_view "
                WHERE `Sample ID` = %(sample_id)s;
            """, { "sample_id": sample_id })
            result = cursor.fetchall()
        result_list = [[str(item) if isinstance(item, datetime.timedelta)
                        else item for item in entry]
                       for entry in result]
        cursor.execute("SHOW COLUMNS FROM master_sample_data_view ;")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result_list, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling sample info from database: {err}")
        return [], []


def filter_by_date(data_type, start_date, end_date):
    """Filters queries by date"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        cursor.execute("""
            SELECT * FROM %(data_type)s
            WHERE `Date Collected` >= %(start_date)s
            AND `Date Collected` <= %(end_date)s;
        """, {
            "data_type": data_type,
            "start_date": start_date,
            "end_date": end_date,
        })
        result = cursor.fetchall()
        cursor.execute("SHOW COLUMNS FROM %(data_type)s;", { "data_type": data_type })
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling sample info from database: {err}")
        return [], []


def get_abund_data(start_date, end_date, sample_type, abundance):
    """Get relative abundance data for graph visualization"""
    _, cursor = initialize_database_cursor()
    try:
        sample_type = f"%{sample_type}%" if sample_type else "%"
        if not start_date:
            start_date = "0000-01-01"
        if not end_date:
            end_date = "9999-12-31"

        cursor.execute("""
            WITH filtered_sample AS (
                SELECT a.`Sample ID`, a.`name`, a.taxonomy_id, a.fraction_total_reads
                FROM sample_data a
                JOIN (
                    SELECT taxonomy_id
                    FROM sample_data
                    GROUP BY taxonomy_id
                    HAVING MAX(fraction_total_reads) > %(abundance)s
                ) b ON a.taxonomy_id = b.taxonomy_id
            ),
            all_data AS (
                SELECT sample_info.`Sample ID` AS 'sample_ID', species.`name` AS 'genus',
                    filtered_sample.fraction_total_reads*100 AS 'value',
                    DATE_FORMAT(submission_data.`Date Collected`, '%Y-%m-%d') AS 'date'
                FROM sample_info
                JOIN filtered_sample ON filtered_sample.`Sample ID` = sample_info.`Sample ID`
                JOIN species ON species.taxonomy_id = filtered_sample.taxonomy_id
                JOIN submission_data
                ON submission_data.`CAHS Submission Number` = sample_info.`CAHS Submission Number`
                WHERE submission_data.`Date Collected` BETWEEN %(start_date)s AND %(end_date)s
                AND sample_info.`Sample Type` LIKE %(sample_type)s
            )
            SELECT all_data.sample_ID, all_data.genus, all_data.`value`,
            all_data.`date`
            FROM all_data
            UNION
            SELECT all_data.sample_ID, 'Unclassified_Bacteria' AS 'genus',
            100-SUM(all_data.`value`) AS 'value', all_data.`date`
            FROM all_data
            GROUP BY sample_ID
            ORDER BY genus, sample_ID
            ;
        """, {
            "abundance": abundance,
            "start_date": start_date,
            "end_date": end_date,
            "sample_type": sample_type,
        })
        if cursor.rowcount:
            return cursor.fetchall()
        return []
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling abund data from database: {err}")
        return []
