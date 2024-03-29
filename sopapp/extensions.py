from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
import os

db = SQLAlchemy()
login_manager = LoginManager()
migration = Migrate()
ckeditor = CKEditor()

### Admin Roles
roles = {
    1: {
        "role" : "admin",
        "desc" : "Add, Update and Delete - Admins, Categories and Products"
        },
    2:{
        "role" : "site admin",
        "desc" : "Add, Update and Delete - Categories and Products"
    },
    3:{
        "role" : "content editor",
        "desc" : "Add, Update and Delete - Products"
    },
    4:{
        "role" : "view only",
        "desc" : "View Categories and Products"
    }
}

### Get Root Directory of project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
params = {
        "blog_name": "SOP Laptops",
        "category_images_upload_path": os.path.join(ROOT_DIR, "static/assets/images/category/"),
        "product_images_upload_path": os.path.join(ROOT_DIR, 'static/assets/images/products/'),
        "blog_images_upload_path": os.path.join(ROOT_DIR, 'static/assets/images/blogs/'),
        "seo": os.path.join(ROOT_DIR, 'seo.json')
    }