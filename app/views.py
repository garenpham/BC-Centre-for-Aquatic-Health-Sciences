"""
Defines view logic for the application server.
"""

import shutil
import os
from functools import wraps
from zipfile import ZipFile

import pandas as pd
import matplotlib.pyplot as plt
from flask import request, abort, flash, render_template, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, \
    current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

from app import app
from .database_push import upload_database, update_sample_info, update_submission_data, \
    update_location_data, delete_location_data, delete_sample_data_data, delete_submission_data
from .database_pull import show_location_data, show_sample_info, show_submission_data, \
    show_sample_data

# from is_safe_url import is_safe_url
# from .database_controller import *
# from app import database_controller


cwd = os.getcwd()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'  # os.environ['SECRET_KEY']
app.config["FILE_UPLOADS"] = cwd + "/app/static/file_uploads"
app.config["ALLOWED_FILE_EXTENSION"] = ["CSV", "HTML", "TXT"]
app.config["MAX_FILESIZE"] = 100 * 1024 * 1024
app.config["CLIENT_DOWNLOADS"] = cwd + "/app/static/file_uploads/download_folder"


def is_admin(func):
    """
    Decorator to check for admin role.
    """

    @wraps(func)
    def admin_decorator(*args, **kwargs):
        if not current_user or current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)

    return admin_decorator


@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the given user ID.
    """

    try:
        return User.query.get(int(user_id))
    # pylint: disable=broad-except
    except BaseException:
        return None


class User(db.Model, UserMixin):
    """
    Defines an entry in the User table.
    """

    # pylint: disable=no-member
    id = db.Column(db.Integer, primary_key=True)

    # pylint: disable=no-member
    username = db.Column(db.String(20), unique=True, nullable=False)

    # pylint: disable=no-member
    password = db.Column(db.String(80), nullable=False)

    # pylint: disable=no-member
    role = db.Column(db.String(20), nullable=True)


class RegisterForm(FlaskForm):
    """
    A Flask form for handling registration.
    """

    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    @staticmethod
    def validation_username(username):
        """Checks to see if there are existing username"""
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "Username is already taken. Re-Enter a new username"
            )


class LoginForm(FlaskForm):
    """
    A Flask form for handling login.
    """

    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@app.route("/", methods=["GET"])
def home():
    """
    Defines the template for rendering the home page.
    """
    return render_template("public/home.html")


@app.route("/about", methods=["GET"])
def about():
    """
    Defines the template for rendering the about page.
    """
    return render_template("public/about.html")


# @app.route("/index", methods=["GET"])
# @login_required
# def index():
#     return render_template("public/index.html", current=current_user.username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Defines the template for rendering the login page.
    """

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(request.args.get('/') or url_for("about"))
            flash('Invalid Username/Password. Please Try again.')
        else:
            flash('User not found.')

    return render_template("public/login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    Defines behavior for handling the logout workflow.
    """

    logout_user()
    flash("Successfully Logged out!!")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Defines the template for rendering the register page.
    """

    form = RegisterForm()
    pin = 'CAHS2022'

    if form.validate_on_submit():
        text = request.form['text']
        if text.upper() == pin.upper():
            hash_pwd = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hash_pwd)

            # pylint: disable=no-member
            db.session.add(new_user)

            # pylint: disable=no-member
            db.session.commit()

            return redirect(url_for('login'))

        flash('Incorrect PIN, please re-enter')

    return render_template("public/register.html", form=form)


@app.route("/index/data", methods=["GET"])
@login_required
def data():
    """
    Defines the template for rendering data visualizations (incomplete).
    """

    try:
        csv_data = pd.read_csv(r'app/static/samples/V0190_Barcode24_Abundances.csv',
            sep=',',
            nrows=10)
    except FileNotFoundError:
        abort(404)
    data_frame = pd.DataFrame(csv_data)

    # chart = data_frame.groupby(['Relative abundance (%)', 'Genera']).size().unstack()
    # chart = pd.crosstab(index=data_frame['Relative abundance (%)'], columns=data_frame['Genera'])
    # chart.plot.bar(stacked=True)
    for genera, abundance in zip(data_frame['Genera'], data_frame['Relative abundance (%)']):
        plt.barh(genera, abundance, 0.75)
    show = plt.show()

    return render_template("public/old.index.html", show=show)


def allow_file(filename):
    """
    Verify that a file's:
        - Name is allowed
        - Extension is allowed
    """
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[-1]
    print(f"This is the extension: {extension}")
    if extension.upper() in app.config["ALLOWED_FILE_EXTENSION"]:
        return True
    return False


def allow_filesize(filesize):
    """
    Verify filesize is less than or equal to global app limit:
    (app.config["MAX_FILESIZE"])
    """
    if int(filesize) <= app.config["MAX_FILESIZE"]:
        return True
    return False


def zip_this(directory):
    """
    compress a directory for future downloads
    """
    file = "zipped_filename.zip"  # filename for compressed output

    with ZipFile(file, 'w') as archive:
        for path, _, files in os.walk(directory):
            for file in files:
                file_name = os.path.join(path, file)
                archive.write(file_name)  # zip the file

    # dont really need this, just to see what we compressed
    print("Contents of the zip file:")
    with ZipFile(file, 'r') as archive:
        archive.printdir()


@app.route("/upload-file", methods=["GET", "POST"])
@login_required
@is_admin

# pylint: disable=too-many-branches
def upload_file():
    """
    Defines the template for rendering the file upload page.
    """

    role = current_user.role
    # pylint: disable=too-many-nested-blocks
    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:

                if not allow_filesize(request.cookies["filesize"]):
                    print("Filesize greater than global limit.")
                    flash("Filesize greater than global limit.")
                    return redirect(request.url)

                file = request.files["file"]

                if file.filename == "":
                    print("Missing filename.")
                    flash("Missing filename.")
                    return redirect(request.url)

                if allow_file(file.filename):
                    sample_id = request.form['Sample ID']
                    secured_file = secure_filename(file.filename)
                    if sample_id is not None or sample_id != "":
                        dir_path = os.path.join(app.config["FILE_UPLOADS"], sample_id)
                        if os.path.isdir(dir_path):
                            file_path = os.path.join(dir_path, secured_file)
                            file.save(file_path)
                            flash("File saved.")
                            if "bracken_report" in secured_file:
                                print("bracken_report triggered")
                                return_message = upload_database(secured_file, sample_id)
                                flash(f"{return_message}")
                        else:
                            try:
                                os.makedirs(dir_path)
                                file.save(os.path.join(dir_path, secured_file))
                                flash("file Saved")
                                if "bracken_report" in secured_file:
                                    print("bracken_report triggered")
                                    return_message = upload_database(secured_file, sample_id)
                                    flash(f"{return_message}")
                            except OSError as error:
                                flash(f"Error saving file{error}")
                    else:
                        flash(f"Missing Sample ID. Unable to write to directory '{sample_id}' ")
                    # print("Saved file to 'app/static/file_uploads'")
                    return redirect(request.url)

                secured_file = secure_filename(file.filename)
                if os.path.isdir(os.path.join(app.config["CLIENT_DOWNLOADS"])):
                    file.save(os.path.join(app.config["CLIENT_DOWNLOADS"], secured_file))
                    flash("File saved.")

                return redirect(request.url)

        # ########### Attempted download function partially broken #####################
        # if request.form.get('submit_button') == "download_file":
        #     print("download_button pushed")
        #     primary_key = request.form.get('sample_id')
        #     if os.path.isdir(os.path.join(app.config["FILE_UPLOADS"], primary_key)):
        #         print("dir exists attempting zip")
        #         zip_this(os.path.join(app.config["FILE_UPLOADS"], primary_key))
        #         try:
        #             return send_from_directory(
        #                   directory=app.config["FILE_UPLOADS"],
        #                   path=f"{primary_key}.zip",
        #             as_attachment=True)
        #         except FileNotFoundError:
        #             abort(404)
        #     return redirect(request.url)

    list_files = []  # File listing implementation that really needs work.
    for folder in os.listdir(app.config["FILE_UPLOADS"]):
        files_contained = os.listdir(os.path.join(app.config["FILE_UPLOADS"], folder))
        list_files.append([folder, files_contained])

    return render_template("public/upload_file.html",
        headers=["Sample ID's", "Files"],
        data=list_files,
        user_role=role)


# class ListStarted():
#     def __init__(self):
#         self.state = 0
#         self.list_files = []
#     def update_files(self):
#         for folder in os.listdir(app.config["FILE_UPLOADS"]):
#             files_contained = os.listdir(os.path.join(app.config["FILE_UPLOADS"], folder))
#             self.list_files.append([folder, files_contained])

# File_list = ListStarted()

@app.route("/metadata", methods=["GET", "POST"])
@login_required
@is_admin
def update_metadata():
    """
    Defines the template for rendering the metadata entry page.
    """

    if request.method == "POST":
        if request.form.get('submit_button') == "update_sample_data":
            return_message, alert_type = update_sample_info(
                sample_id=request.form.get('Sample ID'),
                CAHS_Submission_Number=request.form.get('CAHS Submission Number'),
                sample_Type=request.form.get('Sample Type'),
                sample_Location=request.form.get('Sample location'),
                fish_weight=request.form.get('Fish Weight (g)') or None,
                fish_Length=request.form.get('Fish Length (mm)') or None,
                material_swab=request.form.get('Material Swabbed for Biofilm') or None,
                date_filtered=request.form.get('Date Filtered') or None,
                volume_filtered=request.form.get('Volume Filtered (mL)') or None,
                time_to_filter=request.form.get('Time to Filter (h:mm:ss)') or None
            )
            flash(return_message, alert_type)
            return redirect(request.url)

        if request.form.get('submit_button') == "update_submission_data":
            return_message, alert_type = update_submission_data(
                CAHS_Submission_Number_submission_data=\
                    request.form.get('CAHS Submission Number Submission Data'),
                Samplers=request.form.get('Samplers') or None,
                water_temp=request.form.get('Water Temperature (c)') or None,
                oxygen_measurement=request.form.get('Oxygen (mg/L)') or None,
                saturation_percent=request.form.get('Saturation (%)') or None,
                num_fish_swabs=request.form.get('# Fish Swabs'),
                num_biofilm_swabs=request.form.get('# Biofilm Swabs'),
                num_water_samples_collected=request.form.get('# Water Samples Collected'),
                vol_water=request.form.get('Vol Water collected (mL)'),
                location_id_submission=request.form.get('location_id'),
                date_collected=request.form.get('Date Collected')
            )
            flash(return_message, alert_type)
            return redirect(request.url)

        if request.form.get('submit_button') == "update_location":
            location_id = request.form.get('Location ID')
            location_name = request.form.get('Location Name')
            # exists = check_location_data_exists(location_id)
            return_message, alert_type = update_location_data(location_id, location_name)
            flash(return_message, alert_type)
            return redirect(request.url)

    return render_template("public/metadata.html")


@app.route("/display_data", methods=["GET", "POST"])
@login_required

# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
def show_metadata():
    """
    Defines the template for rendering the database display page.
    """

    role = current_user.role
    if request.method == "GET":
        database_data, header_data = show_sample_info()
        # print(header_data, database_data)
        # database_data, header_data = show_location_data()
        return render_template("public/show_data.html",
            headers=header_data,
            data=database_data,
            user_role=role)

    if request.method == "POST":
        # for the different tabs
        if request.form.get('submit_button') == "sample_info":
            database_data, header_data = show_sample_info()
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        if request.form.get('submit_button') == "location_data":
            database_data, header_data = show_location_data()
            return render_template("public/show_data_location.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        if request.form.get('submit_button') == "submission_data":
            database_data, header_data = show_submission_data()
            return render_template("public/show_data_submission_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        if request.form.get('submit_button') == "sample_data":
            database_data, header_data = show_sample_data()
            return render_template("public/show_data_sample_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # Below is for the delete button
        if (request.form.get('submit_button') == "submit_deleteSample ID"
        and current_user.role == "admin"):
            database_data, header_data = show_sample_info()
            primary_key = request.form.get('sample_id')
            return_message, alert_type = delete_sample_data_data(primary_key)
            # This removes the folder as well on delete
            try:
                file_name_joined = os.path.join(app.config['FILE_UPLOADS'], primary_key)
                shutil.rmtree(file_name_joined)
                print(f"{primary_key} removed successfully")
                return redirect(url_for('downloads'))
            except OSError as error:
                print(error)
                print("File path can not be removed")
            flash(return_message, alert_type)
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # location data
        if (request.form.get('submit_button') == "submit_delete_location"
        and current_user.role == "admin"):
            database_data, header_data = show_location_data()
            primary_key = request.form.get('location_id')
            return_message, alert_type = delete_location_data(primary_key)
            flash(return_message, alert_type)
            return render_template("public/show_data_location.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # submission data
        if (request.form.get('submit_button') == "submit_delete_submission_data"
        and current_user.role == "admin"):
            print('delete triggered')
            database_data, header_data = show_submission_data()
            primary_key = request.form.get('sample_id')
            return_message, alert_type = delete_submission_data(primary_key)
            flash(return_message, alert_type)
            return render_template("public/show_data_submission_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # sample data
        if (request.form.get('submit_button') == "submit_delete_sample_data"
        and current_user.role == "admin"):
            print('delete triggered')
            database_data, header_data = show_sample_data()
            primary_key = request.form.get('sample_id')
            return_message, alert_type = delete_sample_data_data(primary_key)
            # This removes the folder as well on delete
            try:
                file_name_joined = os.path.join(app.config['FILE_UPLOADS'], primary_key)
                shutil.rmtree(file_name_joined)
                print(f"{primary_key} removed successfully")
                return redirect(url_for('downloads'))
            except OSError as error:
                print(error)
                print("File path can not be removed")
            flash(return_message, alert_type)
            return render_template("public/show_data_sample_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # Below is for the edit button ******INCOMPLETE*********
        if (request.form.get('submit_button') == "submit_edit_location"
        and current_user.role == "admin"):
            database_data, header_data = show_location_data()
            primary_key = request.form.get('sample_id')
            # return_message, alert_type = edit_location_data(primary_key)
            # flash(return_message, alert_type)
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        if (request.form.get('submit_button') == "submit_editSample ID"
        and current_user.role == "admin"):
            database_data, header_data = show_sample_info()
            primary_key = request.form.get('sample_id')
            # return_message, alert_type = edit_sample_data_data(primary_key)
            # flash(return_message, alert_type)
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)

    return None


@app.route("/index")
@login_required
def downloads():
    """
    Defines the template for rendering the `Additional Files` page.
    """

    directory = app.config["CLIENT_DOWNLOADS"]
    files = []
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        if os.path.isfile(file):
            files.append(filename)
    # rows = database_controller.get_home_table()
    # return render_template("public/index.html", downloads=downloads, rows = rows)
    return render_template("public/index.html", downloads=files)


@app.route("/index/download/<file_name>")
@login_required
def download_file(file_name):
    """
    Defines behavior for downloading a given file by file name.
    """

    try:
        return send_from_directory(
            directory=app.config["CLIENT_DOWNLOADS"],
            path=file_name,
            as_attachment=True)
    except FileNotFoundError:
        abort(404)
        return None


@app.route("/index/remove/<file_name>")
@login_required
@is_admin
def delete_file(file_name):
    """
    Allows admins to remove files from app/static/file_uploads/download_folder path.
    Upon removing specified file via button on page, user is redirected to
    original downloads route.
    """
    try:
        file_name_joined = os.path.join(app.config['CLIENT_DOWNLOADS'], file_name)
        os.remove(file_name_joined)
        print(f"{file_name} removed successfully")
        return redirect(url_for('downloads'))
    except OSError as error:
        print(error)
        print("File path can not be removed")
        return redirect(url_for('downloads'))


@app.route("/visualization", methods=["GET", "POST"])
@login_required
def show_viz():
    """
    Displays the data visualization page and gets form submission info.
    """
    # role = current_user.role
    if request.form.get('submit_button') == "submit":
        start_date = request.form.get("start-date")
        end_date = request.form.get("end-date")
        # sample_type = request.form.get("sample-type")
        if end_date >= start_date != '' and end_date != '':
            return render_template("public/visualization.html", data="Good-date")
        return render_template("public/visualization.html", data="Bad-date")
    return render_template("public/visualization.html", data=None)