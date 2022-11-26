# ----------- Flask Modules ----------- #
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, IntegerField, FileField, TextAreaField, SelectField, MultipleFileField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

# ----------- Application Modules ----------- #
# from .main import Categories

details = """
[Processor]
(PROCESSOR_NAME)

[Operating System]
(Windows 10 Home)

[Video Card]
(intel® UHD graphics)

[Display]
(Screen Size 14 Inch Touch Screen)

[Memory]
(8GB RAM DDR4)

[Storage]
(SSD 256GB M.2)

[Color]
(Black)

[Keyboard]
(English International backlit keyboard)

[Battery Back Up]
(Good)

[Warranty]
(1 Year)
"""
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
    details = TextAreaField("Product Details", validators=[DataRequired()], default=details)
    pid = HiddenField("product id")
    category = SelectField("Select Product Category", validators=[DataRequired()])
    image_file = MultipleFileField("Upload Product Images", validators=[FileAllowed(['jpg', 'jpeg'], message="Please Upload jpg / jpeg Images")])
    submit = SubmitField("Save", validators=[DataRequired()])

class AddBlog(FlaskForm):
    title = StringField("Blog Title", validators=[DataRequired()])
    metaDesc = TextAreaField("Meta Description", validators=[DataRequired()])
    intro = TextAreaField("Blog Introduction", validators=[DataRequired()])
    image = FileField("Featured Image")
    details = CKEditorField("Blog", validators=[DataRequired()])
    bid = HiddenField("blog id")
    submit = SubmitField("Save", validators=[DataRequired()])