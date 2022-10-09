from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
db = SQLAlchemy()
ckeditor = CKEditor()
from .models.main import Categories
import json

# Project Configuration
with open('D:\Programming and Projects\Projects\Flask\Soplaptops\config.json') as c:
    params = json.load(c)["params"]

# =================================
# Functions
# =================================
# Get Categories
def getCategories(*args):
    if args:
        try:
            categories = Categories.query.filter_by(id=args[0]).first()
            return categories.category # return category name
        except:
            return False
    else:
        try:
            categories = Categories.query.all()
            return categories # return category names
        except Exception as e:
            print(str(e))
            return render_template('error.html', error=str(e))

# Merge two Dictionary
def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

# Subtotal at checkout
def returnSum(dict):
    sum = 0
    for i in dict.values():
        sum = sum + i
    return sum