"""
Defines logic for app initialization.
"""

from flask import Flask
from app import views

app = Flask(__name__)

# from app import database_push
# from app import admin_views
