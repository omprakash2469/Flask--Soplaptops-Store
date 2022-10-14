# ----------- Flask Modules ----------- #
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, SubmitField, PasswordField, HiddenField, EmailField, SelectMultipleField
from wtforms.validators import DataRequired, Email
from datetime import datetime

# ----------- Application Modules ----------- #
from ..extensions import db, roles


# ------------  Database Classes ------------ #
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())

class AdminRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)

# ------------ Form Classess ------------ #
class LoginForm(FlaskForm):
    email = EmailField("Enter Email", validators=[DataRequired(), Email()])
    password = PasswordField("Enter Password", validators=[DataRequired()])
    submit = SubmitField("Login", validators=[DataRequired()])

class AdminAdd(FlaskForm):
    name = StringField("Enter Admin Name", validators=[DataRequired()])
    aid = HiddenField()
    email = EmailField("Enter Admin Email", validators=[DataRequired(), Email()])
    password = PasswordField("Create Admin Password", validators=[DataRequired()])
    roles = SelectMultipleField("Select Role", validators=[DataRequired()], choices=[(r, roles[r]['role']) for r in roles])
    submit = SubmitField("Submit", validators=[DataRequired()])