"""
Defines view logic for the application server.
"""

import csv
import subprocess
import shutil
import os
from functools import wraps
from zipfile import ZipFile

import pandas as pd
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from flask import make_response, request, abort, flash, render_template, session, url_for, \
    redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, \
    current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

from app import app
from .functions import generate_csv, sanitize_form_data
from .database_push import upload_database, update_sample_info, update_submission_data, \
    update_location_data, delete_location_data, delete_sample_data_data, delete_submission_data
from .database_pull import show_sample_data, show_hatchery_data, show_environmental_data, \
    get_all_sample_data, get_hatcheries, get_sample_by_sample_id, \
    get_submission_by_submission_no, get_abund_data, filter_by_date
from .file_metadata import locate_file_metadata, read_file_metadata, write_file_metadata

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
app.config["ALLOWED_FILE_EXTENSION"] = ["CSV", "HTML", "TXT"]
app.config["MAX_FILESIZE"] = 100 * 1024 * 1024
app.config["FILE_UPLOADS"] = os.path.join(cwd, "..", "file_uploads")
app.config["CLIENT_DOWNLOADS"] = os.path.join(cwd, "..", "file_uploads", "download_folder")


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

# pylint: disable=too-many-branches,too-many-return-statements
def upload_file():
    """
    Defines the template for rendering the file upload page.
    """

    if request.method == "POST":
        if not request.files:
            flash("Failed to upload file: `request.files` field is nullish", "danger")
            return redirect(request.url)

        if "file_size" not in request.form:
            flash("Failed to upload file: No filesize provided", "danger")
            return redirect(request.url)

        if not allow_filesize(request.form["file_size"]):
            flash("Failed to upload file: File size greater than global limit.", "danger")
            return redirect(request.url)

        file = request.files["file"]

        if not file.filename:
            flash("Failed to upload file: Missing filename", "danger")
            return redirect(request.url)

        if request.form["file_type"] == "sample":
            if not allow_file(file.filename):
                flash("Failed to upload file: File extension is invalid", "danger")
                return redirect(request.url)

            sample_id = request.form["sample_id"]
            if not sample_id:
                flash(f"Missing Sample ID. Unable to write to directory '{sample_id}'", "danger")
                return redirect(request.url)

            file_name = secure_filename(file.filename)
            dir_path = os.path.join(app.config["FILE_UPLOADS"], sample_id)
            file_path = os.path.join(dir_path, file_name)
            if not os.path.isdir(dir_path):
                try:
                    os.makedirs(dir_path)
                except OSError as error:
                    flash(f"Error saving file: {error}", "danger")
                    return redirect(request.url)

            # need to save file in order to load into db
            file.save(file_path)

            if "bracken_report" in file_name:
                return_message = upload_database(file_name, sample_id)
                if "error" in return_message:
                    # no need to keep invalid sample uploads
                    os.remove(file_path)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                    flash(return_message, "danger")
                else:
                    flash(return_message, "info")

            return redirect(request.url)

        # file extension is not "allowed": assume file is a document
        dir_path = app.config["CLIENT_DOWNLOADS"]
        file_name = secure_filename(file.filename)
        file_path = os.path.join(dir_path, file_name)
        if os.path.isdir(dir_path):
            file.save(file_path)
            flash("File saved.", "info")

        write_file_metadata(file_path,
            title=request.form.get("document_title"),
            description=request.form.get("document_description"))

        return redirect(request.url)


    list_files = []
    for folder in os.listdir(app.config["FILE_UPLOADS"]):
        files_contained = os.listdir(os.path.join(app.config["FILE_UPLOADS"], folder))
        list_files.append([folder, files_contained])

    return render_template("public/upload_file.html",
        headers=["Sample ID's", "Files"],
        data=list_files,
        user_role=current_user.role)


# class ListStarted():
#     def __init__(self):
#         self.state = 0
#         self.list_files = []
#     def update_files(self):
#         for folder in os.listdir(app.config["FILE_UPLOADS"]):
#             files_contained = os.listdir(os.path.join(app.config["FILE_UPLOADS"], folder))
#             self.list_files.append([folder, files_contained])

# File_list = ListStarted()

# pylint: disable=invalid-name,too-many-locals, too-many-statements
@app.route("/metadata", methods=["GET"])
@login_required
@is_admin
def update_metadata():
    """
    Defines the template for rendering the metadata entry page.
    """
    return render_template("public/metadata.html", hatcheries=get_hatcheries())


@app.route("/update_environmental_data", methods=["POST"])
@login_required
@is_admin
def update_environmental_data():
    """
    API endpoint for updating environmental data
    """
    return_message, alert_type = update_submission_data(**sanitize_form_data(request.form))
    return make_response(jsonify({
        "message": return_message,
        "category": alert_type,
    }), 200)


@app.route("/update_sample_data", methods=["POST"])
@login_required
@is_admin
def update_sample_data():
    """
    API endpoint for updating sample data
    """
    return_message, alert_type = update_sample_info(**sanitize_form_data(request.form))
    return make_response(jsonify({
        "message": return_message,
        "category": alert_type,
    }), 200)


@app.route("/update_hatchery_data", methods=["POST"])
@login_required
@is_admin
def update_hatchery_data():
    """
    API endpoint for updating hatchery data
    """
    return_message, alert_type = update_location_data(**request.form)
    return make_response(jsonify({
        "message": return_message,
        "category": alert_type,
    }), 200)


@app.route("/sample_data/<sample_id>")
@login_required
def get_sample_data(sample_id):
    """
    API endpoint for retrieving sample data by sample ID
    """

    sample_data = get_sample_by_sample_id(sample_id)
    if not sample_data:
        return make_response(f"No sample data found for '{sample_id}'", 404)

    sample_data = dict(zip([
        "sampleId",
        "submissionNo",
        "sampleType",
        "sampleLocation",
        "fishWeight",
        "fishLength",
        "biofilmMaterial",
        "waterDateFiltered",
        "waterVolFiltered",
        "waterTimeToFilter",
    ], sample_data[0]))
    return make_response(jsonify(sample_data), 200)


@app.route("/environmental_data/<submission_no>")
@login_required
def get_environmental_data(submission_no):
    """
    API endpoint for retrieving environmental data by CAHS submission number
    """

    sample_data = get_submission_by_submission_no(submission_no)
    if not sample_data:
        return make_response(f"No environmental data found for '{submission_no}'", 404)

    sample_data = dict(zip([
        "submissionNo",
        "samplers",
        "waterTemperature",
        "oxygen",
        "saturation",
        "fishSwabs",
        "biofilmSwabs",
        "waterSamples",
        "waterVolPerSample",
        "hatcheryId",
        "dateCollected",
    ], sample_data[0]))
    return make_response(jsonify(sample_data), 200)

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
        database_data, header_data = get_all_sample_data()
        session["database_data"] = database_data
        session["database_headers"] = header_data
        session["data_type"] = "master_sample_data_view"
        # print(header_data, database_data)
        # database_data, header_data = show_location_data()
        return render_template("public/show_data.html",
            headers=header_data,
            data=database_data,
            user_role=role)

    if request.method == "POST":
        # for the different tabs
        if request.form.get('submit_button') == "all_data":
            database_data, header_data = get_all_sample_data()
            session["database_data"] = database_data
            session["database_headers"] = header_data
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role)
        if request.form.get('submit_button') == "sample_data":
            database_data, header_data = show_sample_data()
            session["database_data"] = database_data
            session["database_headers"] = header_data
            return render_template("public/show_data_sample.html",
                headers=header_data,
                data=database_data,
                user_role=role)
        if request.form.get('submit_button') == "environmental_data":
            database_data, header_data = show_environmental_data()
            session["database_data"] = database_data
            session["database_headers"] = header_data
            return render_template("public/show_data_environmental.html",
                headers=header_data,
                data=database_data,
                user_role=role)
        if request.form.get('submit_button') == "hatchery_data":
            database_data, header_data = show_hatchery_data()
            session["database_data"] = database_data
            session["database_headers"] = header_data
            return render_template("public/show_data_hatchery.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # Below is for the delete button
        # location data
        if (request.form.get('submit_button') == "submit_delete_location"
        and current_user.role == "admin"):
            primary_key = request.form.get('location_id')
            return_message, alert_type = delete_location_data(primary_key)
            flash(return_message, alert_type)
            database_data, header_data = show_hatchery_data()
            return render_template("public/show_data_hatchery.html",
                headers=header_data,
                data=database_data,
                user_role=role)
        # submission data
        if (request.form.get('submit_button') == "submit_delete_submission_data"
        and current_user.role == "admin"):
            print('delete triggered')
            primary_key = request.form.get('sample_id')
            return_message, alert_type = delete_submission_data(primary_key)
            flash(return_message, alert_type)
            database_data, header_data = show_environmental_data()
            return render_template("public/show_data_environmental.html",
                headers=header_data,
                data=database_data,
                user_role=role)
        # sample data
        if (request.form.get('submit_button') == "submit_delete_sample_data"
        and current_user.role == "admin"):
            print('delete triggered')
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
            database_data, header_data = show_sample_data()
            return render_template("public/show_data_sample.html",
                headers=header_data,
                data=database_data,
                user_role=role)

        # Download current selection
        if request.form.get('submit_button') == "submit_download":
            return app.response_class(generate_csv(session["database_data"],
                session["database_headers"]),
                mimetype='text/csv')
        # Download single row of data
        if request.form.get('submit_button') == "submit_downloadSample ID":
            download_data, download_header_data = get_all_sample_data(primary_key)
            return app.response_class(generate_csv(download_data, download_header_data),
                mimetype='text/csv')
        # Filter Selection
        if request.form.get('submit_button') == "submit_filter":
            print('filtering')
            database_data, header_data = filter_by_date(session["data_type"],
                request.form.get('start-date'),
                request.form.get('end-date'))
            session["database_data"] = database_data
            return render_template("public/show_data.html",
                headers=header_data,
                data=database_data,
                user_role=role,
                filter=f"{request.form.get('start-date')} to {request.form.get('end-date')}")
    return None


@app.route("/documents", methods=["GET", "POST"])
@login_required
def downloads():
    """
    Defines the template for rendering the `Documents` page.
    """

    # POST handles updating document metadata
    if request.method == "POST":
        file_name = request.form.get("file_name")
        file_path = os.path.join(app.config["CLIENT_DOWNLOADS"], file_name)
        write_file_metadata(file_path,
            title=request.form.get("document_title"),
            description=request.form.get("document_description"))
        flash(f"The file '{file_name}' was updated successfully.", "info")
        return redirect(request.url)


    directory = app.config["CLIENT_DOWNLOADS"]
    files = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        file = read_file_metadata(file_path)
        if file:
            files.append(file)

    return render_template("public/documents.html", downloads=files)


@app.route("/documents/download/<file_name>")
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


@app.route("/documents/delete/<file_name>")
@login_required
@is_admin
def delete_file(file_name):
    """
    Allows admins to delete files from the path specified by `app.config['CLIENT_DOWNLOADS']`.
    Upon removing specified file via button on page, user is redirected to
    original downloads route.
    """
    try:
        file_path = os.path.join(app.config['CLIENT_DOWNLOADS'], file_name)
        os.remove(file_path)

        meta_path = locate_file_metadata(file_path)
        os.remove(meta_path)

        flash(f"The file '{file_name}' was deleted successfully.", "info")
        return redirect(url_for("downloads"))
    except OSError as error:
        flash(f"Failed to remove '{file_name}': {error}", "danger")
        return redirect(url_for("downloads"))


@app.route("/visualization", methods=["GET", "POST"])
@login_required
def show_viz():
    """
    Displays the data visualization page and gets form submission info.
    """
    if request.method == "POST":
        start_date = request.form.get("start-date") or None
        end_date = request.form.get("end-date") or None
        sample_type = request.form["sample-type"] if request.form["sample-type"] != "All" else None
        abundance = int(request.form.get("abund-slider")) * 0.005

        current_working_dir = os.getcwd()
        abund_data_result = get_abund_data(start_date, end_date, sample_type, abundance)

        if not abund_data_result:
            return make_response(jsonify({"message":"Empty"}), 200)

        with open("app/r/rel_abund_long.csv", encoding="utf-8", mode="w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["sample_ID", "genus", "value", "date"])
            csv_writer.writerows(abund_data_result)

        try:
            subprocess.run(["/usr/bin/Rscript", f"{current_working_dir}/app/r/abund_graphs.R"],
            check=True)
        except subprocess.CalledProcessError:
            return make_response(jsonify({"message":"Error"}), 500)

        return make_response(jsonify({
            "message":"OK",
            "viz1":"data_abund_separate.png",
            "viz2":"data_abund_grouped.png"
            }), 200)
    return render_template("public/visualization.html")
