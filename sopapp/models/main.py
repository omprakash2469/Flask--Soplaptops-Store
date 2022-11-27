# ----------- Flask Modules ----------- #
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email
from datetime import datetime
from ..extensions import db


# ------------  Database Classes ------------ #
class Emails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250), nullable=False)
    tagline = db.Column(db.String(500), nullable=False)
    category_img = db.Column(db.String(250), nullable=False)

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    metaDesc = db.Column(db.Text)
    intro = db.Column(db.Text)
    image = db.Column(db.String(500), nullable=False)
    details = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, default='text')
    views = db.Column(db.Integer, default=0)
    date = db.Column(db.Integer, default=datetime.now())
    admin_id = db.Column(db.Integer, nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(250), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.Text, default="text")
    category_id = db.Column(db.Integer, nullable=False)

class ProductsImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(250), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

# ------------ Form Classess ------------ #
class EmailForm(FlaskForm):
    email = EmailField("subscribe", validators=[DataRequired(), Email("Please Enter a Valid Email Address")])
    submit = SubmitField("Subscribe", validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    email = EmailField("Enter Your Email", validators=[DataRequired(), Email()])
    location = StringField("Enter Your Location", validators=[DataRequired()])
    subject = StringField("Your Subject", validators=[DataRequired()])
    message = TextAreaField("Enter Your Message", validators=[DataRequired()])
    submit = SubmitField("Submit")