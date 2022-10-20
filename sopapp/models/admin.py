# ----------- Flask Modules ----------- #
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, IntegerField, FileField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField

# ----------- Application Modules ----------- #
# from .main import Categories


# ------------ Form Classess ------------ #
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
    pid = HiddenField("product id")
    category = SelectField("Select Product Category", validators=[DataRequired()])
    image_file = MultipleFileField("Upload Product Images", validators=[FileAllowed(['jpg', 'jpeg'], message="Please Upload jpg / jpeg Images")])
    submit = SubmitField("Save", validators=[DataRequired()])