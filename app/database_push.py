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
        cursor.execute(
            """
            SELECT `sample_id` FROM sample_info
            WHERE `sample_id` LIKE %(sample_id)s;
        """,
            {"sample_id": sample_id},
        )
        if not cursor.rowcount:
            return (
                "Upload to database failed error:"
                f" No corresponding sample data found for sample ID '{sample_id}'"
            )

        # delete preexisting bracken report data
        cursor.execute(
            """
            SELECT `sample_id` FROM sample_data
            WHERE `sample_id` LIKE %(sample_id)s;
        """,
            {"sample_id": sample_id},
        )
        if cursor.rowcount:
            cursor.execute(
                """
                DELETE FROM sample_data
                WHERE `sample_id` LIKE %(sample_id)s;
            """,
                {"sample_id": sample_id},
            )
            database.commit()

        cursor.execute(
            """
            LOAD DATA LOCAL INFILE %(file_path)s INTO TABLE sample_data
            FIELDS TERMINATED BY '\t'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES (
                `name`, `taxonomy_id`, `taxonomy_lvl`, `kraken_assigned_reads`,
                `added_reads`, `new_est_reads`, `fraction_total_reads`
            ) SET `sample_id` = %(sample_id)s;
        """,
            {
                "file_path": file_path,
                "sample_id": sample_id,
            },
        )
        database.commit()
        return f"Uploaded '{file_name}' to database successfully."
    except mysql.connector.Error as err:
        print(f"Something went wrong with uploading to sample_data: {err}")
        return f"Upload to database failed error: {err}"


# pylint: disable=too-many-arguments, too-many-locals, invalid-name
def update_sample_info(
    sample_id,
    CAHS_Submission_Number,
    sample_Type,
    sample_Location,
    fish_weight,
    fish_Length,
    material_swab,
    date_filtered,
    volume_filtered,
    time_to_filter,
):
    """
    At the moment the database upload is fairly basic but it will do an insert need to add a try and
    except to control this.
    """
    database, cursor = initialize_database_cursor()
    print(
        sample_id,
        CAHS_Submission_Number,
        sample_Type,
        sample_Location,
        fish_weight,
        fish_Length,
        material_swab,
        date_filtered,
        volume_filtered,
        time_to_filter,
    )
    try:
        cursor.execute(
            "SELECT `sample_id` FROM sample_info WHERE `sample_id` LIKE %(sample_id)s;",
            {"sample_id": sample_id},
        )
        number_rows = cursor.rowcount
        if number_rows == 0:
            sample_info = (
                "INSERT INTO sample_info (`sample_id`, `submission_id`, `sample_type`, "
                "`sample_location`, `fish_weight_g`, `fish_length_mm`, "
                "`biofilm_swab_mat`, `date_filtered`, `volume_filtered_ml`, "
                "`fiter_time`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(
                sample_info,
                (
                    sample_id,
                    CAHS_Submission_Number,
                    sample_Type,
                    sample_Location,
                    fish_weight,
                    fish_Length,
                    material_swab,
                    date_filtered,
                    volume_filtered,
                    time_to_filter,
                ),
            )
            database.commit()
            database_error = f"Sample ID: {sample_id} added"
            alert_type = "success"
        else:
            update_query = (
                "UPDATE sample_info SET `submission_id` = %s, `sample_type` = %s, "
                "`sample_location` = %s, `fish_weight_g` = %s, `fish_length_mm` = %s, "
                "`biofilm_swab_mat` = %s, `date_filtered` = %s, "
                "`volume_filtered_ml` = %s, `fiter_time` = %s "
                "WHERE `sample_id` = %s "
            )
            print(update_query)
            cursor.execute(
                update_query,
                (
                    CAHS_Submission_Number,
                    sample_Type,
                    sample_Location,
                    fish_weight,
                    fish_Length,
                    material_swab,
                    date_filtered,
                    volume_filtered,
                    time_to_filter,
                    sample_id,
                ),
            )
            database.commit()
            database_error = f"Sample ID: {sample_id} updated"
            alert_type = "info"
        return database_error, alert_type
    except mysql.connector.Error as err:
        print(f"Something went wrong with uploading to sample_info: {err}")
        database_error = f"Something went wrong with uploading to sample_info: {err}"
        alert_type = "danger"
        return database_error, alert_type


# pylint: disable=too-many-arguments, too-many-locals
def update_submission_data(
    CAHS_Submission_Number_submission_data,
    Samplers,
    water_temp,
    oxygen_measurement,
    saturation_percent,
    num_fish_swabs,
    num_biofilm_swabs,
    num_water_samples_collected,
    vol_water,
    location_id_submission,
    date_collected,
):
    """Adds submission data to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "SELECT `submission_id` FROM submission_data WHERE `CAHS Submission Number` "
            "LIKE %(CAHS_Submission_Number)s;",
            {"CAHS_Submission_Number": CAHS_Submission_Number_submission_data},
        )
        number_rows = cursor.rowcount
        if number_rows == 0:
            submission_info = (
                "INSERT INTO submission_data (`submission_id`, `samplers`, "
                "`water_temp_c`, `oxygen`, `saturation_percent`, `num_fish_swabs`, "
                "`num_biofilm_swabs`, `num_water_samples`, `volume_collected_ml`, "
                "`location_id`, `date_collected`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(
                submission_info,
                (
                    CAHS_Submission_Number_submission_data,
                    Samplers,
                    water_temp,
                    oxygen_measurement,
                    saturation_percent,
                    num_fish_swabs,
                    num_biofilm_swabs,
                    num_water_samples_collected,
                    vol_water,
                    location_id_submission,
                    date_collected,
                ),
            )
            database.commit()
            database_error = (
                f"Submission Number: {CAHS_Submission_Number_submission_data} added"
            )
            alert_type = "success"
        else:
            update_submission_info = (
                "UPDATE submission_data SET `submission_id` = %s, `samplers` = %s, "
                "`water_temp_c` = %s, `oxygen` = %s, `saturation_percent` = %s, "
                "`num_fish_swabs` = %s, `num_biofilm_swabs` = %s, `num_water_samples` = %s, "
                "`volume_collected_ml` = %s, `location_id` = %s, "
                "`date_collected` = %s WHERE `submission_id` = %s "
            )
            cursor.execute(
                update_submission_info,
                (
                    CAHS_Submission_Number_submission_data,
                    Samplers,
                    water_temp,
                    oxygen_measurement,
                    saturation_percent,
                    num_fish_swabs,
                    num_biofilm_swabs,
                    num_water_samples_collected,
                    vol_water,
                    location_id_submission,
                    date_collected,
                    CAHS_Submission_Number_submission_data,
                ),
            )
            database.commit()
            database_error = (
                f"Submission Number: {CAHS_Submission_Number_submission_data} updated"
            )
            alert_type = "info"
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = (
            f"Something went wrong with uploading to submission data: {err}"
        )
        alert_type = "danger"
        return database_error, alert_type


def check_location_data_exists(location_id):
    """Check if the location Data exists already"""
    # pylint: disable=unused-variable
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "SELECT `location_id` FROM location "
            "WHERE `location_id` LIKE %(location_id)s;",
            {"location_id": location_id},
        )
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
        cursor.execute(
            "SELECT `location_id` FROM location "
            "WHERE `location_id` LIKE %(location_id)s;",
            {"location_id": location_id},
        )
        number_rows = cursor.rowcount
        if number_rows == 0:
            location_info = (
                "INSERT INTO location (`location_id`, `site_name`) VALUES (%s, %s)"
            )
            cursor.execute(location_info, (location_id, location_name))
            database.commit()
            database_error = f"added new location {location_name} id: {location_id}"
            alert_type = "success"
        else:
            update_location_info = (
                "UPDATE location SET `location_id` = %s, `site_name` = %s "
                "WHERE `location_id` = %s "
            )
            cursor.execute(
                update_location_info, (location_id, location_name, location_id)
            )
            database.commit()
            database_error = (
                f"Updated Location id: {location_id} Name: {location_name} "
            )
            alert_type = "info"
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with uploading to location data: {err}"
        alert_type = "danger"
        return database_error, alert_type


def delete_location_data(location_id):
    """Delete location data to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "DELETE FROM location WHERE `location_id` = %(location_id)s;",
            {"location_id": location_id},
        )
        database.commit()
        database_error = f"Deleted Location id: {location_id}"
        alert_type = "success"
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting location data: {err}"
        alert_type = "danger"
        return database_error, alert_type


def delete_sample_data_data(sample_id):
    """Delete sample_data and sample_info to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "DELETE FROM sample_data WHERE `sample_id` = %(sample_id)s;",
            {"sample_id": sample_id},
        )
        cursor.execute(
            "DELETE FROM sample_info WHERE `sample_id` = %(sample_id)s;",
            {"sample_id": sample_id},
        )
        database.commit()
        database_error = f"Deleted Sample id: {sample_id}"
        alert_type = "success"
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting Sample Data: {err}"
        alert_type = "danger"
        return database_error, alert_type


def delete_submission_data(CAHS_Submission_Number):
    """Delete submission data using the primary key CAHS_Sumbission_Number to the database"""
    database, cursor = initialize_database_cursor()
    try:
        cursor.execute(
            "DELETE FROM sample_info "
            "WHERE `submission_id` = %(CAHS_Submission_Number)s;",
            {"CAHS_Submission_Number": CAHS_Submission_Number},
        )
        cursor.execute(
            "DELETE FROM submission_data "
            "WHERE `submission_id` = %(CAHS_Submission_Number)s;",
            {"CAHS_Submission_Number": CAHS_Submission_Number},
            
        )
        database.commit()
        database_error = f"Deleted CAHS Submission Number: {CAHS_Submission_Number}"
        alert_type = "success"
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = f"Something went wrong with Deleting Sample Data: {err}"
        alert_type = "danger"
        return database_error, alert_type
