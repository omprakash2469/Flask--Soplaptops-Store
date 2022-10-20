# ----------- Flask Modules ----------- #
from email.policy import default
from flask import session
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, EmailField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email
from datetime import datetime

# ----------- Application Modules ----------- #
from ..extensions import db

# ------------  Database Classes ------------ #
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    number = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    street = db.Column(db.String(500), default='')
    zipcode = db.Column(db.Integer, default=0)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0)
    order_date = db.Column(db.DateTime, default=datetime.now())

# ------------ Form Classess ------------ #
class OrdersForm(FlaskForm):
    name = StringField("Your Full Name", validators=[DataRequired()])
    number = StringField("Phone Number", validators=[DataRequired()])
    street = StringField("Street", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    zipcode = StringField("zipcode", validators=[DataRequired()])
    place_order = SubmitField("Place Order")

class UserRegisterForm(FlaskForm):
    name = StringField("Your Full Name", validators=[DataRequired()])
    number = StringField("Phone Numebr", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    cpassword = PasswordField("Confirm Password", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    signup = SubmitField("Sign Up", validators=[DataRequired()])

class UserUpdateForm(FlaskForm):
    id = HiddenField('uid', validators=[DataRequired()])
    name = StringField("Full Name", validators=[DataRequired()])
    number = StringField("Contact", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[DataRequired()])
    street = StringField("Street")
    zipcode = StringField("zipcode")
    update = SubmitField("Update", validators=[DataRequired()])