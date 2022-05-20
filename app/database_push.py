"""
Defines logic for pushing to the database.
"""

import os
import mysql.connector
from app import app
from .database_controller import initialize_database_cursor


def upload_database(file_name, sample_id):
    """
    At the moment the database upload is fairly basic but it will do an insert need to add a try and
    except to control this.
    """

    dir_path = app.config["FILE_UPLOADS"]
    file_path = os.path.join(dir_path, sample_id, file_name)

    database, cursor = initialize_database_cursor()
    try:
        # constraint: sample_data rows must have corresponding entries in sample_info table
        cursor.execute(f"SELECT `Sample ID` FROM sample_info WHERE `Sample ID` LIKE '{sample_id}';")
        if not cursor.rowcount:
            return ("Upload to database failed error:"
                f" No corresponding sample data found for sample ID '{sample_id}'")

        # delete preexisting bracken report data
        cursor.execute(f"SELECT `Sample ID` FROM sample_data WHERE `Sample ID` LIKE '{sample_id}';")
        if cursor.rowcount:
            cursor.execute(f"DELETE FROM sample_data WHERE `Sample ID` LIKE '{sample_id}';")
            database.commit()

        cursor.execute(f"""
            LOAD DATA LOCAL INFILE '{file_path}' INTO TABLE sample_data
            FIELDS TERMINATED BY '\t'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES (
                `name`, `taxonomy_id`, `taxonomy_lvl`, `kraken_assigned_reads`,
                `added_reads`, `new_est_reads`, `fraction_total_reads`
            ) SET `Sample ID` = '{sample_id}';
        """)
        database.commit()
        return f"Uploaded '{file_name}' to database successfully."
    except mysql.connector.Error as err:
        print(f"Something went wrong with uploading to sample_data: {err}")
        return f"Upload to database failed error: {err}"


# pylint: disable=too-many-arguments, too-many-locals, invalid-name
def update_sample_info(sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight,
                       fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter):
    """
    At the moment the database upload is fairly basic but it will do an insert need to add a try and
    except to control this.
    """
    database, cursor = initialize_database_cursor()
    print(sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length,
          material_swab, date_filtered, volume_filtered, time_to_filter)
    try:
        cursor.execute("SELECT `Sample ID` FROM sample_info WHERE `Sample ID` LIKE %(sample_id)s;" ,
            {'sample_id': sample_id})
        number_rows = cursor.rowcount
        if number_rows == 0:
            sample_info = (
                "INSERT INTO sample_info (`Sample ID`, `CAHS Submission Number`, `Sample Type`, "
                "`Sample location`, `Fish Weight (g)`, `Fish Length (mm)`, "
                "`Material Swabbed for Biofilm`, `Date Filtered`, `Volume Filtered (mL)`, "
                "`Time to Filter (h:mm:ss)`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(sample_info, (
                sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight,
                fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter))
            database.commit()
            database_error = f"Sample ID: {sample_id} added"
            alert_type = 'success'
        else:
            update_query = (
                "UPDATE sample_info SET `CAHS Submission Number` = %s, `Sample Type` = %s, "
                "`Sample location` = %s, `Fish Weight (g)` = %s, `Fish Length (mm)` = %s, "
                "`Material Swabbed for Biofilm` = %s, `Date Filtered` = %s, "
                "`Volume Filtered (mL)` = %s, `Time to Filter (h:mm:ss)` = %s "
                "WHERE `Sample ID` = %s ")
            print(update_query)
            cursor.execute(update_query, (
                CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length,
                material_swab, date_filtered, volume_filtered, time_to_filter, sample_id))
            database.commit()
            database_error = f"Sample ID: {sample_id} updated"
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        print(f"Something went wrong with uploading to sample_info: {err}")
        database_error = f"Something went wrong with uploading to sample_info: {err}"
        alert_type = 'danger'
        return database_error, alert_type


# pylint: disable=too-many-arguments, too-many-locals
def update_submission_data(CAHS_Submission_Number_submission_data, Samplers, water_temp,
                           oxygen_measurement, saturation_percent, num_fish_swabs,
                           num_biofilm_swabs, num_water_samples_collected, vol_water,
                           location_id_submission, date_collected):
    """Adds submission data to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "SELECT `CAHS Submission Number` FROM submission_data WHERE `CAHS Submission Number` "
            "LIKE %(CAHS_Submission_Number)s;" ,
            {'CAHS_Submission_Number': CAHS_Submission_Number_submission_data})
        number_rows = cursor.rowcount
        if number_rows == 0:
            submission_info = (
                "INSERT INTO submission_data (`CAHS Submission Number`, `Samplers`, "
                "`Water Temperature (c)`, `Oxygen (mg/L)`, `Saturation (%)`, `# Fish Swabs`, "
                "`# Biofilm Swabs`, `# Water Samples Collected`, `Vol Water collected (mL)`, "
                "`location_id`, `Date Collected`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(submission_info, (
                CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement,
                saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected,
                vol_water, location_id_submission, date_collected))
            database.commit()
            database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} added"
            alert_type = 'success'
        else:
            update_submission_info = (
                "UPDATE submission_data SET `CAHS Submission Number` = %s, `Samplers` = %s, "
                "`Water Temperature (c)` = %s, `Oxygen (mg/L)` = %s, `Saturation (%)` = %s, "
                "`# Fish Swabs` = %s, `# Biofilm Swabs` = %s, `# Water Samples Collected` = %s, "
                "`Vol Water collected (mL)` = %s, `location_id` = %s, "
                "`Date Collected` = %s WHERE `CAHS Submission Number` = %s ")
            cursor.execute(update_submission_info, (
                CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement,
                saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected,
                vol_water, location_id_submission, date_collected,
                CAHS_Submission_Number_submission_data))
            database.commit()
            database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} updated"
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with uploading to submission data: {err}"
        alert_type = 'danger'
        return database_error, alert_type


def check_location_data_exists(location_id):
    """Check if the location Data exists already"""
    # pylint: disable=unused-variable
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute("SELECT `location_id` FROM location "
                       "WHERE `location_id` LIKE %(location_id)s;",
                       {'location_id': location_id})
        return cursor.rowcount > 0
    except mysql.connector.Error:
        return False


def update_location_data(location_id, location_name):
    """Adds location data to the database"""
    database, cursor = initialize_database_cursor()
    try:
        # if location_id == "" and location_name != "":
        #     cursor.execute("SELECT `Sample ID` FROM sample_info "
        #                    "WHERE `Sample ID` LIKE %(sample_id)s;",
        #                    {'sample_id': sample_id})
        # elif location_name == "" and location_id != "":
        #     cursor.execute("SELECT `Sample ID` FROM sample_info "
        #                    "WHERE `Sample ID` LIKE %(sample_id)s;",
        #                    {'sample_id': sample_id})
        # else:
        cursor.execute("SELECT `location_id` FROM location "
                       "WHERE `location_id` LIKE %(location_id)s;",
                       {'location_id': location_id})
        number_rows = cursor.rowcount
        if number_rows == 0:
            location_info = "INSERT INTO location (`location_id`, `site_name`) VALUES (%s, %s)"
            cursor.execute(location_info, (location_id, location_name))
            database.commit()
            database_error = f"added new location {location_name} id: {location_id}"
            alert_type = 'success'
        else:
            update_location_info = ("UPDATE location SET `location_id` = %s, `site_name` = %s "
                                   "WHERE `location_id` = %s ")
            cursor.execute(update_location_info, (location_id, location_name, location_id))
            database.commit()
            database_error = f"Updated Location id: {location_id} Name: {location_name} "
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with uploading to location data: {err}"
        alert_type = 'danger'
        return database_error, alert_type


def delete_location_data(location_id):
    """Delete location data to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute("DELETE FROM location WHERE `location_id` = %(location_id)s;",
                       {'location_id': location_id})
        database.commit()
        database_error = f"Deleted Location id: {location_id}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting location data: {err}"
        alert_type = 'danger'
        return database_error, alert_type


def delete_sample_data_data(sample_id):
    """Delete sample_data and sample_info to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute("DELETE FROM sample_data WHERE `Sample ID` = %(sample_id)s;",
            {'sample_id': sample_id})
        cursor.execute("DELETE FROM sample_info WHERE `Sample ID` = %(sample_id)s;",
            {'sample_id': sample_id})
        database.commit()
        database_error = f"Deleted Sample id: {sample_id}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting Sample Data: {err}"
        alert_type = 'danger'
        return database_error, alert_type


def delete_submission_data(CAHS_Submission_Number):
    """Delete submission data using the primary key CAHS_Sumbission_Number to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute("DELETE FROM sample_info "
                       "WHERE `CAHS Submission Number` = %(CAHS_Submission_Number)s;",
                       {'CAHS_Submission_Number': CAHS_Submission_Number})
        cursor.execute("DELETE FROM submission_data "
                       "WHERE `CAHS Submission Number` = %(CAHS_Submission_Number)s;",
                       {'CAHS_Submission_Number': CAHS_Submission_Number})
        database.commit()
        database_error = f"Deleted CAHS Submission Number: {CAHS_Submission_Number}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting Sample Data: {err}"
        alert_type = 'danger'
        return database_error, alert_type
