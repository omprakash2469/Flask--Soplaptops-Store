from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField, IntegerField, FileField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField
from datetime import datetime

from ..extensions import db
from .main import Categories


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.String(500), nullable=False)

class AdminRole(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)

# ------------ Form Classess ------------ 
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login", validators=[DataRequired()])

class AddCategory(FlaskForm):
    category = StringField("Category", validators=[DataRequired()])
    tagline = StringField("Tagline", validators=[DataRequired()])
    image = StringField("Category Image Name", validators=[DataRequired()])
    image_file = FileField("Upload Image", validators=[FileAllowed(['jpg', 'png'], message="Please Upload webp Image")])
    cid = HiddenField("category id")
    submit = SubmitField("Save", validators=[DataRequired()])

class AddProduct(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired()])
    desc = TextAreaField("Product Description", validators=[DataRequired()])
    price = IntegerField("Price", validators=[DataRequired()])
    stock = IntegerField("Stock", validators=[DataRequired()])
    details = CKEditorField("Product Details", validators=[DataRequired()])
    category = SelectField("Select Product Category", validators=[DataRequired()], choices=[(c.id, c.category) for c in Categories.query.all()])
    image_file = MultipleFileField("Upload Product Images", validators=[FileAllowed(['jpg', 'jpeg'], message="Please Upload jpg / jpeg Images")])
    submit = SubmitField("Save", validators=[DataRequired()])