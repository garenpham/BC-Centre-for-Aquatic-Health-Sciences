import mysql.connector
import pandas as pd
import os

def mysql_database_connection():
    '''MySQL Database Connection'''
    try:
        db = mysql.connector.connect(
            host =  os.environ['DB_HOST'],
            port = os.environ['DB_PORT'],
            user = os.environ['DB_USER'],
            passwd = os.environ['DB_PASS'],
            auth_plugin = os.environ['DB_AUTH_PLUGIN'],
            database = os.environ['DB'],
        )
    except mysql.connector.Error as err:
        print(f"error connecting to the database. please verify that MySQL is running.{err}")
        exit()
    return db



def upload_database(file_name, sample_id):
    '''At the moment the database upload is fairly basic but it will do an insert need to add a try and except to control this.'''

    #requires changes to --secure-file-priv location
    # file_name and sample_ID at the moment are static strings for testing purposes
    cwd = os.getcwd()
    file_location = os.path.join(cwd, "app", "static", "file_uploads", sample_id, file_name)
    print("file location: ", file_location)

    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)

    try:
        cursor.execute("SELECT `Sample ID` FROM sample_data WHERE `Sample ID` LIKE %(sample_id)s;", {'sample_id': sample_id})
        #pushing to the sample_data database
        #may be /r/n or /n depending on the system and how it is pushed once on github it becomes /r/n though
        number_rows = cursor.rowcount
        if number_rows != 0:
            cursor.execute("DELETE FROM sample_data WHERE `Sample ID` LIKE %(sample_id)s;", {'sample_id': sample_id})
            db.commit()
        #Executes the load data if no pre-existing data exists need to add confirmation at some point
        load = ("LOAD DATA LOCAL INFILE %s INTO TABLE sample_data FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n' IGNORE 1 LINES (`name`, `taxonomy_id`, `taxonomy_lvl`, "
        "`kraken_assigned_reads`, `added_reads`, `new_est_reads`, `fraction_total_reads`) SET `Sample ID` = (%s);")
        cursor.execute(load, (file_location, sample_id))
        db.commit()
        return f"Upload of Bracken report Successful"
    except mysql.connector.Error as err:
        return f"Upload to database failed error: {err}"
        print("Something went wrong with uploading to sample_data: {}".format(err))



def update_sample_info(sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter):
    '''At the moment the database upload is fairly basic but it will do an insert need to add a try and except to control this.'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    print(sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter)
    try:
        cursor.execute("SELECT `Sample ID` FROM sample_info WHERE `Sample ID` LIKE %(sample_id)s;", {'sample_id': sample_id})
        number_rows = cursor.rowcount
        if number_rows == 0:
            sample_info = ("INSERT INTO sample_info (`Sample ID`, `CAHS Submission Number`, `Sample Type`, `Sample location`, `Fish Weight (g)`, `Fish Length (mm)`, "
            "`Material Swabbed for Biofilm`, `Date Filtered`, `Volume Filtered (mL)`, `Time to Filter (h:mm:ss)`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(sample_info, (sample_id, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter))
            db.commit()
            database_error = f"Sample ID: {sample_id} added"
            alert_type = 'success'
        else:
            update_sample_info = ("UPDATE sample_info SET `CAHS Submission Number` = %s, `Sample Type` = %s, `Sample location` = %s, `Fish Weight (g)` = %s, `Fish Length (mm)` = %s, "
            "`Material Swabbed for Biofilm` = %s, `Date Filtered` = %s, `Volume Filtered (mL)` = %s, `Time to Filter (h:mm:ss)` = %s WHERE `Sample ID` = %s ")
            print(update_sample_info)
            cursor.execute(update_sample_info, (CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter, sample_id))
            db.commit()
            database_error = f"Sample ID: {sample_id} updated"
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        print("Something went wrong with uploading to sample_info: {}".format(err))
        database_error = "Something went wrong with uploading to sample_info: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type

def update_submission_data(CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement, saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected, vol_water, location_id_submission, date_collected):
    '''Adds submission data to the database'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT `CAHS Submission Number` FROM submission_data WHERE `CAHS Submission Number` LIKE %(CAHS_Submission_Number)s;", {'CAHS_Submission_Number': CAHS_Submission_Number_submission_data})
        number_rows = cursor.rowcount
        if number_rows == 0:
            submission_info = ("INSERT INTO submission_data (`CAHS Submission Number`, `Samplers`, `Water Temperature (c)`, `Oxygen (mg/L)`, `Saturation (%)`, `# Fish Swabs`, "
            "`# Biofilm Swabs`, `# Water Samples Collected`, `Vol Water collected (mL)`, `location_id`, `Date Collected`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(submission_info, (CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement, saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected, vol_water, location_id_submission, date_collected))
            db.commit()
            database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} added"
            alert_type = 'success'
        else:
            update_submission_info = ("UPDATE submission_data SET `CAHS Submission Number` = %s, `Samplers` = %s, `Water Temperature (c)` = %s, `Oxygen (mg/L)` = %s, `Saturation (%)` = %s, "
            "`# Fish Swabs` = %s, `# Biofilm Swabs` = %s, `# Water Samples Collected` = %s, `Vol Water collected (mL)` = %s, `location_id` = %s, `Date Collected` = %s WHERE `CAHS Submission Number` = %s ")
            cursor.execute(update_submission_info, (CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement, saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected, vol_water, location_id_submission, date_collected, CAHS_Submission_Number_submission_data))
            db.commit()
            database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} updated"
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = "Something went wrong with uploading to submission data: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type


def check_location_data_exists(location_id):
    '''Check if the location Data exists already'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT `location_id` FROM location WHERE `location_id` LIKE %(location_id)s;", {'location_id': location_id})
        number_rows = cursor.rowcount
        if number_rows > 0:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        return False

def update_location_data(location_id, location_name):
    '''Adds location data to the database'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        # if location_id == "" and location_name != "":
        #     cursor.execute("SELECT `Sample ID` FROM sample_info WHERE `Sample ID` LIKE %(sample_id)s;", {'sample_id': sample_id})
        # elif location_name == "" and location_id != "":
        #     cursor.execute("SELECT `Sample ID` FROM sample_info WHERE `Sample ID` LIKE %(sample_id)s;", {'sample_id': sample_id})
        # else:
        cursor.execute("SELECT `location_id` FROM location WHERE `location_id` LIKE %(location_id)s;", {'location_id': location_id})
        number_rows = cursor.rowcount
        if number_rows == 0:
            location_info = ("INSERT INTO location (`location_id`, `site_name`) VALUES (%s, %s)")
            cursor.execute(location_info, (location_id, location_name))
            db.commit()
            database_error = f"added new location {location_name} id: {location_id}"
            alert_type = 'success'
        else:
            update_location_info = ("UPDATE location SET `location_id` = %s, `site_name` = %s WHERE `location_id` = %s ")
            cursor.execute(update_location_info, (location_id, location_name, location_id))
            db.commit()
            database_error = f"Updated Location id: {location_id} Name: {location_name} "
            alert_type = 'info'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = "Something went wrong with uploading to location data: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type

def delete_location_data(location_id):
    '''Delete location data to the database'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM location WHERE `location_id` = %(location_id)s;", {'location_id': location_id})
        db.commit()
        database_error = f"Deleted Location id: {location_id}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = "Something went wrong with Deleting location data: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type


def delete_sample_data_data(sample_id):
    '''Delete sample_data and sample_info to the database'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM sample_data WHERE `Sample ID` = %(sample_id)s;", {'sample_id': sample_id})
        cursor.execute("DELETE FROM sample_info WHERE `Sample ID` = %(sample_id)s;", {'sample_id': sample_id})
        db.commit()
        database_error = f"Deleted Sample id: {sample_id}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = "Something went wrong with Deleting Sample Data: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type

def delete_submission_data(CAHS_Submission_Number):
    '''Delete submission data using the primary key CAHS_Sumbission_Number to the database'''
    try:
        db = mysql_database_connection()
    except:
        print(f"error connecting to the database. please verify that MySQL is running.")
        exit()

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("DELETE FROM sample_info WHERE `CAHS Submission Number` = %(CAHS_Submission_Number)s;", {'CAHS_Submission_Number': CAHS_Submission_Number})
        cursor.execute("DELETE FROM submission_data WHERE `CAHS Submission Number` = %(CAHS_Submission_Number)s;", {'CAHS_Submission_Number': CAHS_Submission_Number})
        db.commit()
        database_error = f"Deleted CAHS Submission Number: {CAHS_Submission_Number}"
        alert_type = 'success'
        return database_error, alert_type
    except mysql.connector.Error as err:
        database_error = "Something went wrong with Deleting Sample Data: {}".format(err)
        alert_type = 'danger'
        return database_error, alert_type
# def Sumbission_data_custom_view(sample_id, CAHS_Submission_Number, sample_Type, sample_Location, water_temp, oxygen_measurement, saturation_percent, location_id, location_name):
#     '''Adds submission data to the database'''
#     try:
#         db = mysql_database_connection()
#     except:
#         print(f"error connecting to the database. please verify that MySQL is running.")
#         exit()

#     cursor = db.cursor(buffered=True)
#     try:
#         cursor.execute("SELECT `CAHS Submission Number` FROM submission_data WHERE `CAHS Submission Number` LIKE %(CAHS_Submission_Number)s;", {'CAHS_Submission_Number': CAHS_Submission_Number_submission_data})
#         number_rows = cursor.rowcount
#         if number_rows == 0:
#             submission_info = ("INSERT INTO submission_data (`CAHS Submission Number`, `Samplers`, `Water Temperature (c)`, `Oxygen (mg/L)`, `Saturation (%)`, `# Fish Swabs`, "
#             "`# Biofilm Swabs`, `# Water Samples Collected`, `Vol Water collected (mL)`, `location_id`, `Date Collected`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
#             cursor.execute(submission_info, (CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement, saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected, vol_water, location_id_submission, date_collected))
#             db.commit()
#             database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} added"
#             alert_type = 'success'
#         else:
#             update_submission_info = ("UPDATE submission_data SET `CAHS Submission Number` = %s, `Samplers` = %s, `Water Temperature (c)` = %s, `Oxygen (mg/L)` = %s, `Saturation (%)` = %s, "
#             "`# Fish Swabs` = %s, `# Biofilm Swabs` = %s, `# Water Samples Collected` = %s, `Vol Water collected (mL)` = %s, `location_id` = %s, `Date Collected` = %s WHERE `CAHS_Submission_Number` = %s ")
#             cursor.execute(update_submission_info, (CAHS_Submission_Number_submission_data, Samplers, water_temp, oxygen_measurement, saturation_percent, num_fish_swabs, num_biofilm_swabs, num_water_samples_collected, vol_water, location_id_submission, date_collected, CAHS_Submission_Number_submission_data))
#             db.commit()
#             database_error = f"Submission Number: {CAHS_Submission_Number_submission_data} updated"
#             alert_type = 'info'
#         return database_error, alert_type
#     except mysql.connector.Error as err:
#         database_error = "Something went wrong with uploading to submission data: {}".format(err)
#         alert_type = 'danger'
#         return database_error, alert_type




'''Ignore text below here only preserved for future reference if required.'''

# metadata_name = "Quinsam_Hatchery_Sample_Data_Updated_Feb8_2022.xlsx"



# metadata_location = os.path.join("C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads", metadata_name)

# xls = pd.ExcelFile(metadata_location)
# df1 = pd.read_excel(xls, sheet_name=0)
# df2 = pd.read_excel(xls, sheet_name=1)
# print(df2)
# f = open("test_file.txt", "w")
# text = df2.to_string()
# f.write(df2.to_string())
# f.close()
#connecting to mysql
# def upload_database(file_name, sample_id, date_collected, location, CAHS_Submission_Number, sample_Type, sample_Location, fish_weight, fish_Length, material_swab, date_filtered, volume_filtered, time_to_filter):
#     # file_name = "barcode18.bracken_report.txt"
#     # sample_ID = "barcode18"
#     cwd = os.getcwd()
#     file_location = os.path.join(cwd, "static", "file_uploads", file_name)
#     try:
#         db = mysql.connector.connect(
#             host="localhost",
#             port=3306,
#             user="root",
#             passwd="Acit3910test",
#             auth_plugin="mysql_native_password"
#         )
#     except mysql.connector.Error as err:
#         print(f"error connecting to the database. please verify that MySQL is running.")
#         exit()
#     cursor = db.cursor()
#     cursor.execute("INSERT INTO TABLE bio_database.sample_info (`Sample ID`, `CAHS Submission Number`, `Sample Type`, `Sample location`, `Fish Weight (g)`, `Fish Length (mm)`, `Material Swabbed for Biofilm`, `Date Filtered`, `Volume Filtered (mL)`, `Time to Filter (h:mm:ss)`) VALUES (%(sample_id)s, %(date_collected)s, %(location)s, %(CAHS_Submission_Number)s, %(sample_Type)s, %(sample_Location)s, %(fish_weight)s, %(fish_Length)s, %(material_swab)s, %(date_filtered)s, %(volume_filtered)s, %(time_to_filter)s)", {'sample_id': sample_id, 'date_collected': date_collected, 'location': location, 'CAHS_Submission_Number': CAHS_Submission_Number, 'sample_Type': sample_Type, 'sample_Location': sample_Location, 'fish_weight': fish_weight, 'fish_Length': fish_Length, 'material_swab': material_swab, 'date_filtered': date_filtered, 'volume_filtered': volume_filtered, 'time_to_filter': time_to_filter})
#     cursor.execute("LOAD DATA INFILE %(file_location)s INTO TABLE bio_database.sample_data FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n' IGNORE 1 LINES (`name`, `taxonomy_id`, `taxonomy_lvl`, `kraken_assigned_reads`, `added_reads`, `new_est_reads`, `fraction_total_reads`) SET `Sample ID` = (%(sample_id)s);", {'sample_id': sample_id, 'file_location': file_location})
#     db.commit()
