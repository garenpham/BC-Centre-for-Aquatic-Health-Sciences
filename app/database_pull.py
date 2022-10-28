"""
Defines logic for pulling from the database.
"""
import datetime

import mysql.connector

from app.constants import END_OF_TIME, START_OF_TIME
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
    Gets sample data by sample_id
    """

    _, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT * FROM sample_info WHERE sample_id LIKE %(sample_id)s;",
                       {"sample_id": sample_id})
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling sample data from database: {err}")
        return []


def get_submission_by_submission_no(submission_no):
    """
    Gets environmental data by submission_id
    """

    _, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT * FROM submission_data"
                       " WHERE submission_id LIKE %(submission_no)s;",
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
    """Queries for all sample data, can be by sample_id"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        if sample_id is None:
            cursor.execute("SELECT * FROM master_sample_data_view ;")
            result = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT * FROM master_sample_data_view "
                WHERE sample_id = %(sample_id)s;
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


def filter_by_date(data_view, start_date, end_date):
    """Filters queries by date"""
    _, cursor = initialize_database_cursor()
    try:
        headers = []
        cursor.execute(f"""
            SELECT * FROM {data_view}
            WHERE date_collected BETWEEN %(start_date)s AND %(end_date)s;
        """, {
            "start_date": start_date,
            "end_date": end_date
        })
        result = cursor.fetchall()
        result_list = [[str(item) if isinstance(item, datetime.timedelta)
                        else item for item in entry]
                       for entry in result]
        cursor.execute(f"SHOW COLUMNS FROM {data_view};")
        headers_list = cursor.fetchall()
        for row in headers_list:
            headers.append(row[0])
        return result_list, headers
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling sample info from database: {err}")
        return [], []


def get_abund_data(start_date, end_date, sample_type, abundance):
    """Get relative abundance data for graph visualization"""
    _, cursor = initialize_database_cursor()
    try:
        sample_type = f"%{sample_type}%" if sample_type else "%"
        if not start_date:
            start_date = START_OF_TIME
        if not end_date:
            end_date = END_OF_TIME

        cursor.execute("""
            WITH filtered_sample AS (
                SELECT a.sample_id, a.`name`, a.taxonomy_id, a.fraction_total_reads
                FROM sample_data a
                JOIN (
                    SELECT taxonomy_id
                    FROM sample_data
                    GROUP BY taxonomy_id
                    HAVING MAX(fraction_total_reads) > %(abundance)s
                ) b ON a.taxonomy_id = b.taxonomy_id
            ),
            all_data AS (
                SELECT sample_info.sample_id AS 'sample_ID', species.`name` AS 'genus',
                    filtered_sample.fraction_total_reads*100 AS 'value',
                    DATE_FORMAT(submission_data.date_collected, '%Y-%m-%d') AS 'date'
                FROM sample_info
                JOIN filtered_sample ON filtered_sample.sample_id = sample_info.sample_id
                JOIN species ON species.taxonomy_id = filtered_sample.taxonomy_id
                JOIN submission_data
                ON submission_data.submission_id = sample_info.submission_id
                WHERE submission_data.date_collected BETWEEN %(start_date)s AND %(end_date)s
                AND sample_info.sample_type LIKE %(sample_type)s
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

def get_trend_data(start_date, end_date, sample_type, abundance, species_array):
    """Get Trend of Relative Abundance for One or More Species Over Time"""
    _, cursor = initialize_database_cursor()
    try:
        sample_type = f"%{sample_type}%" if sample_type != 'All' else "%"
        if not start_date:
            start_date = START_OF_TIME
        if not end_date:
            end_date = END_OF_TIME
        if species_array == []:
            species_array = ""
        #print("MULTI LINE:", species_array)
        cursor.execute("""
            SELECT
                t3.name, #as 'Name',
                --   t3.taxonomy_id, #as 'Taxonomy ID',
                --   t3.sample_id, #as 'Sample ID',
                --   t3.submission_id,
                --   t3.sample_type,
                AVG(t3.fraction_total_reads) as 'fraction_total_reads',
                -- t3.sample_location, # as 'Sample Location',
                t4.date_collected # as 'Date Collected'
                FROM  
                (SELECT
                    t1.name,
                    t1.taxonomy_id,
                    t1.fraction_total_reads,
                    t1.sample_id,
                    t2.submission_id,
                    t2.sample_type,
                    t2.sample_location
                FROM 
                    (SELECT
                    sample_data.name,
                    sample_data.taxonomy_id,
                    sample_data.fraction_total_reads,
                    sample_data.sample_id
                    FROM sample_data
                    WHERE name = 'Haliscomenobacter' OR name = 'Polaromonas') t1 
                    INNER JOIN
                    (SELECT
                    sample_info.sample_id,
                    sample_info.submission_id,
                    sample_info.sample_type,
                    sample_info.sample_location
                    FROM sample_info
                    WHERE sample_type LIKE %(sample_type)s) t2
                    ON t1.sample_id = t2.sample_id) t3
                LEFT JOIN
                (SELECT
                submission_data.submission_id,
                submission_data.date_collected
                FROM submission_data) t4
                ON t3.submission_id = t4.submission_id
                GROUP BY name, date_collected;
                        """, {
            "abundance": abundance,
            "start_date": start_date,
            "end_date": end_date,
            "sample_type": sample_type,
            "species_array": species_array,
        })
        # Example Species Array String
        # "WHERE name = 'Haliscomenobacter' OR name = 'Polaromonas'"
        print(cursor.rowcount)
        if cursor.rowcount:
            return cursor.fetchall()    
        return []
    except mysql.connector.Error as err:
        print(f"Something went wrong pulling abund data from database: {err}")
        return []
