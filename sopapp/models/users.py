# ----------- Flask Modules ----------- #
from enum import unique
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, EmailField
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
    city = db.Column(db.String(250), nullable=False) 
    state = db.Column(db.String(250), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0)
    order_date = db.Column(db.DateTime, default=datetime.now())

# ------------ Form Classess ------------ #
class OrdersForm(FlaskForm):
    name = StringField("Your Full Name", validators=[DataRequired()])
    number = StringField("Phone Numebr", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    street = StringField("Street", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    zipcode = StringField("zipcode", validators=[DataRequired()])
    place_order = SubmitField("Place Order")
