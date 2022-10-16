from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
import json

db = SQLAlchemy()
ckeditor = CKEditor()

### Project Configuration
with open('D:\Programming and Projects\Projects\Flask\Soplaptops\config.json') as c:
    params = json.load(c)["params"]

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