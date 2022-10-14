# ----------- Flask Modules ----------- #
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from wtforms.validators import DataRequired
from datetime import datetime

# ----------- Application Modules ----------- #
from ..extensions import db

# ------------  Database Classes ------------ #
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
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
class AddToCart(FlaskForm):
    id = HiddenField('Product Id', validators=[DataRequired()])
    quantity = HiddenField('Quantity', validators=[DataRequired()], default=1)
    add = SubmitField('Add to Cart', validators=[DataRequired()])
