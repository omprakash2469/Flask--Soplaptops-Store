from itertools import product
from math import prod
from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, HiddenField, EmailField, TextAreaField, SelectField, IntegerField, MultipleFileField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from datetime import datetime
import json
import os

# Site Variable
with open('config.json', "r") as c:
    params = json.load(c)["params"]

# Instantiate Flask app
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Configuration
app.secret_key = params['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = params['database_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Database Configuration
db = SQLAlchemy(app)

# ------------ Database Models ------------------
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

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250), nullable=False)
    tagline = db.Column(db.String(500), nullable=False)
    category_img = db.Column(db.String(250), nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(250), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

class ProductsImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(250), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Emails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

# ------------ Form Classes ------------------
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login", validators=[DataRequired()])

class EmailForm(FlaskForm):
    email = EmailField("subscribe", validators=[DataRequired(), Email("Please Enter a Valid Email Address")])
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
            return categories # return category name
        except:
            return False

def NumberOfProducts(id):
    try:
        query = Products.query.filter_by(category_id=id).count()
        return query
    except:
        return False

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


# ============================================
# ============
# Front Endpoints 
# ============
# ============================================
@app.route("/", methods = ['GET', 'POST'])
def index():
    form = EmailForm()
    # Add Email to database
    if form.validate_on_submit():
        email = form.email.data
        try:
            entry = Emails(email=email)
            db.session.add(entry)
            db.session.commit()
            flash("Thanks to subscribe! We will let you know Best Deals on laptops", "text-green-600")
            return redirect('/#subscribe')
        except:
            flash("Please Try Again!!", "text-red-500")
            return redirect('/#subscribe')

    return render_template('home.html',
                params=params,
                categories=getCategories(),
                form=form
            )


# Product Archive pages
@app.route('/products/<string:category>')
def shop(category):
    # Validate if category exists
    try:
        query = Categories.query.filter_by(category=category.lower()).first()
        if query:
            cid = query.id
    except Exception as e:
        flash("Unexpected Error Occured", "text-red-500")
        return redirect(url_for('error'))

    # Get Products
    try:
        query = Products.query.filter_by(category_id=cid).all()
    except:
        flash("Products Not Found", "text-red-500")
        return redirect(url_for('error'))

    products = {}
    k = 0
    for i in query:
        k += 1
        products[k] = {}
        products[k] = {
            "id": i.id,
            "name": i.product,
            "price": i.price,
            "image": ProductsImages.query.filter_by(product_id=i.id).first()
        }
    
    if products=={}: products = False

    return render_template('shop.html',
                params=params,
                categories=getCategories(),
                category=category,
                products=products, 
                )

# Single products
@app.route("/products/<string:category>/<string:slug>")
def singleProductPage(category, slug):
    category = category.capitalize()
    product_name = slug.replace('-', ' ').lower()

    try:
        # Fetch product details
        slug = slug.replace('-', ' ').lower()
        products = Products.query.filter_by(product=product_name).first()
        images = ProductsImages.query.filter_by(product_id=products.id).all()
        details = {
                "id": products.id,
                "product": products.product,
                "desc": products.product_desc,
                "price": products.price,
                "stock": products.stock,
                "details": products.details,
                "category": category.lower(),
                "urls": images
        }
    except:
        flash("Product Not Found", "text-red-500")
        return redirect(url_for('error'))

    # Fetch related product details
    related = Products.query.limit(5)
    rProducts = {}
    k = 0
    for i in related:
        k += 1
        rProducts[k] = {}
        image = ProductsImages.query.filter_by(product_id=i.id).first()
        rProducts[k] = {
                "id": i.id,
                "name": i.product,
                "price": i.price,
                "image": image.image_name
            }
    
    return render_template('product.html', params=params, details=details, rProducts=rProducts, categories=getCategories())

# Cart
@app.route("/cart", methods=['GET', 'POST'])
def addCart():
    product_id = request.form.get('product_id')
    category = request.form.get('category')
    quantity = request.form.get('quantity')
    if product_id and category and quantity and request.method == 'POST':
        product = eval(category.capitalize()).query.filter_by(id=product_id).first()
        cartItems = {
            product_id : {
                'category': category,
                'name': product.product_name,
                'price': product.price,
                'quantity': quantity
            }
        }
        # Store products in session
        if 'shoppingCart' in session:
            print(session['shoppingCart'])
            if product_id in session['shoppingCart']:
                print("This product is already in cart")
            else:
                session['shoppingCart'] = MergeDicts(session['shoppingCart'], cartItems)
                return redirect(request.referrer)
        else:
            session['shoppingCart'] = cartItems
            return redirect(request.referrer) 

    if session.get('shoppingCart') == None:
        return render_template('empty-cart.html', params=params, categories=categories)

    return render_template('cart.html', params=params, categories=categories)

# Remove Cart Item
@app.route("/del", methods=['GET', 'POST'])
def delCartItem():
    pid = request.form.get('product_id')
    category = request.form.get('category')
    if pid and category and session['shoppingCart'][pid]['category'] == category:
        session['shoppingCart'].pop(pid, None)
        session.modified = True
    else:
        return render_template('error.html', msg="Internal Server Error")

    return redirect(request.referrer)

# Get Category Id With Name
def categoryIdWithName(id):
    if id:
        categoryName = Categories.query.filter_by(category_name=id).first()
        return categoryName.id
    else:
        return False
    

# Checkout
@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    # Check if product are added in cart
    if session['shoppingCart'] == {}:
        msg = "Please select product to proceed to checkout"
        return render_template('cart.html', params=params, msg=msg)
    
    return render_template('checkout.html', params=params)

# Orders
@app.route("/orders", methods=['GET', 'POST'])
def orders():
    if session['shoppingCart'] == {}:
        return redirect("/cart")

    fname = request.form.get('name')
    fphone = request.form.get('phone')
    femail = request.form.get('email')
    faddress = request.form.get('address')
    fstreet = request.form.get('street')
    fzipcode = request.form.get('zipcode')
    fcity = request.form.get('city')

    if fname and fphone and femail and faddress and fstreet and fzipcode and fcity and request.method == "POST":
        orders = Orders(
            name = fname,
            phone = fphone,
            email = femail,
            address = faddress,
            street_nearby = fstreet,
            zipcode = fzipcode,
            city = fcity
        )
        db.session.add(orders)
        db.session.commit()
        db.session.flush()

        lastId = orders.id

        for i in session['shoppingCart']:
            customer = Customers(
                customer_id = lastId,
                qty = session['shoppingCart'][i]['quantity'],
                order_status = 0,
                category_id = categoryIdWithName(session['shoppingCart'][i]['category']),
                product_id = i
            )
            db.session.add(customer)
            db.session.commit()
        return render_template('confirmation.html', params=params, msg=True, categories=categories)
    else:
        msg = "Please Enter Delivery Details"
        return render_template('checkout.html', params=params, msg=msg, categories=categories)

# 
@app.route("/trackorder")
def trackorder():
    trackid = request.form.get('trackid')
    return render_template('order.html', params=params)

# About
@app.route("/about")
def about():
    return render_template('about.html', params=params, categories=getCategories())

# Contact Us
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=="POST"):
        # Add Entry To Database
        fname = request.form.get('name')
        femail = request.form.get('email')
        flocation = request.form.get('location')
        fsubject = request.form.get('subject')
        fmessage = request.form.get('message')

        if fname and femail and fsubject and flocation and fmessage :
            try:
                entry = Contact(name=fname, email=femail, location=flocation, subject=fsubject, message=fmessage)
                db.session.add(entry)
                db.session.commit()
                flash("Successfully Send! We will contact you soon", "text-green-500")
                return redirect(url_for('contact'))
            except:
                flash("Unexpected Error Occured", "text-red-600")
                return redirect(url_for('contact'))
        else:
            flash("Please Enter Details", "text-red-600")
            return redirect(url_for('contact'))

    return render_template('contact.html', params=params, categories=getCategories())








# ============================================
# ============
# Back Endpoints 
# ============
# ============================================
# ----------- Admin and Dashboard -----------
@app.route("/admin", methods=['GET', 'POST'])
# ----------- Login -----------
def admin():
    form = LoginForm()
    # Log in user
    if 'user' in session and session['loggedin']:
        return render_template('admin/index.html', params=params, categories=getCategories())

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if(username == params['admin'] and password == params['admin_password']):
            # Setting session variable
            session['user'] = username
            session['loggedin'] = True
            return redirect(url_for('admin'))

    return render_template('auth/login.html', params=params, form=form)

# ----------- Logout -----------
@app.route('/admin/logout/')
def logout():
    session.pop('user',None)
    session.pop('loggedin',None)
    return redirect(url_for('admin'))

# ----------- Account -----------
@app.route('/admin/account/')
def adminAccount():
    return render_template('admin/account.html', params=params, categories=getCategories())

# ----------- Categories -----------
@app.route("/admin/categories", methods = ['GET', 'POST'])
# Display Categories
def categories():
    form = AddCategory()
    vars = {
        "title": "Add New Category",
        "action": url_for('addCategories')
    }
    return render_template('admin/category.html',
        params=params,
        form=form,
        vars=vars,
        categories=getCategories()
    )

# Adding Categories
@app.route("/admin/categories/add", methods = ['GET', 'POST'])
def addCategories():
    form = AddCategory()
    if form.validate_on_submit():
        # Adding New Category
        category = form.category.data
        tagline = form.tagline.data
        imgname = form.image.data
        imagefile = form.image_file.data

        # -- Create Image filename
        imageName = imgname.strip().lower().replace(' ', '-') + os.path.splitext(imagefile.filename)[1]
        # -- Save Image file
        imagefile.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName)))
        # -- Add record in Table
        entry = Categories(category=category.lower(), tagline=tagline, category_img=secure_filename(imageName))
        db.session.add(entry)
        db.session.commit()
        flash("Successfully! Added Category", "alert-success")
        return redirect(url_for('categories'))
    else:
        return redirect(url_for('error'))

# Editing Categories
@app.route("/admin/categories/edit", methods = ['GET', 'POST'])
def editCategories():
    form = AddCategory()
    if form.validate_on_submit():
        # Update Category
        cid = form.cid.data
        category = form.category.data
        tagline = form.tagline.data
        imgname = form.image.data
        imagefile = form.image_file.data
        data = Categories.query.filter_by(id=cid).first()

       # ----- Check if Image is uploaded
        if imagefile != None:
            # Create Image filename
            imageName = imgname.strip().lower().replace(' ', '-') + os.path.splitext(imagefile.filename)[1]
            oldImageName = data.category_img
            # Check if file exists
            imagePath = params['category_images_upload_path']+ oldImageName
            if os.path.exists(imagePath):
                os.remove(imagePath) # Remove old image
                imagefile.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName))) # Upload New Image
        else:
            # Create Image filename
            ext = os.path.splitext(data.category_img)[1]
            imageName = imgname.strip().lower().replace(' ', '-') + ext
            src = params['category_images_upload_path'] + data.category_img
            dest = params['category_images_upload_path'] + imageName
            os.rename(src, dest)
 
        # ----- Update record in Table
        data.category = category
        data.tagline = tagline
        data.category_img = imageName
        db.session.commit()
        flash("Successfully! Updated Category", "alert-success")
        return redirect(url_for('categories'))
    else:
        flash("Unexpected Error Occured", "alert-danger")
        return redirect(url_for('categories'))

# Deleting Categories
@app.route("/admin/categories/delete", methods = ['GET', 'POST'])
def deleteCategories():
    # Delete Categories
    if request.method == "POST" and request.form.get('cid')!='':
        cid = request.form.get('cid')
        categories = Categories.query.filter_by(id=cid).first()
        # Delete Category Image
        imagepath = os.path.join(params['category_images_upload_path'], categories.category_img)
        if os.path.exists(imagepath):
            os.remove(imagepath)
        # Delete category from table
        db.session.delete(categories)
        db.session.commit()
        flash('Deleted Successfully', 'alert-danger')
        return redirect(url_for('categories'))
    else:
        return redirect(url_for('error'))


# ----------- Products -----------
# Display Product Categories
@app.route("/product")
def adminProducts():
    return render_template('admin/product-categories.html',params=params, categories=getCategories())

# Display Product Archives Page
@app.route("/product/<string:category>")
def adminProductPage(category):
    try:
        query = Categories.query.filter_by(category=category.lower()).first()
        cid = query.id
    except Exception as e:
        flash('Category Not Exists', 'alert-danger')
        return redirect(url_for('error'))

    queryProducts = Products.query.filter_by(category_id=cid).all()
    products = {}
    i = 0
    for p in queryProducts:
        products[i] = {
            "id" : p.id,
            "product": p.product,
            "desc": p.product_desc,
            "price": p.price,
            "stocks": p.stock,
            "details": p.details,
            "category": p.category_id,
            "images": ProductsImages.query.filter_by(product_id=p.id).all()
        }
        i+=1

    return render_template('admin/product.html', params=params, categories=getCategories(), category=query.category, products=products)

# Add New Product
@app.route("/product/add", methods=['GET', 'POST'])
def adminAddProduct():
    form = AddProduct()
    if form.validate_on_submit():
        # Get form values
        fproduct_name = form.product_name.data
        fdesc = form.desc.data
        fprice = form.price.data
        fstock = form.stock.data
        fdetails = form.details.data
        fcategory = form.category.data
        fimage_file = form.image_file.data

        # Get category id by category
        try:
            category = Categories.query.filter_by(id=fcategory).first()
            category = category.category
        except Exception as e:
            return redirect(url_for('error'))


        # Insert into database
        entry = Products(
            product = fproduct_name.lower(),
            product_desc = fdesc,
            price = fprice,
            stock = fstock,
            details = fdetails,
            category_id = fcategory
        )
        db.session.add(entry)
        db.session.commit()
        db.session.flush()
        pid = entry.id

        # Upload product images
        for img in fimage_file:
            # create folder if doesn't exists
            if (os.path.isdir(params['product_images_upload_path'] + category + '/') == False):
                os.makedirs(params['product_images_upload_path'] + category + '/', exist_ok=True)
            image = secure_filename(img.filename)
            img.save(os.path.join(params['product_images_upload_path'] + category + "/", image))
            insertImage = ProductsImages(
                image_name = image,
                product_id = pid
            )
            db.session.add(insertImage)
            db.session.commit()

        flash("Successfully! Added New Product", "alert-success")
        return redirect(url_for('adminProductPage', category=category))
    vars = {
        "title": "Add New Product",
        "action": url_for('adminAddProduct'),
        "product_name": "",
        "desc": "",
        "price": "",
        "stock": "",
        "details": "",
        "category": "",
        "button": "Submit"
    }

    return render_template('admin/add-product.html',params=params, categories=getCategories(), form=form, vars=vars)

# Edit Product
@app.route("/product/edit", methods=['GET', 'POST'])
def adminEditProduct():
    form = AddProduct()
    if request.method == "POST" and request.form.get('action') == 'editform' and request.form.get('pid'):
        pid = request.form.get('pid')
        query = Products.query.filter_by(id=pid).first()
        vars = {
        "title": "Update Product",
        "action": url_for('adminEditProduct'),
        "product_name": query.product,
        "desc": query.product_desc,
        "price": query.price,
        "stock": query.stock,
        "details": query.details,
        "category": query.category_id,
        "button": "Update"
        }
        return render_template('admin/add-product.html',params=params, categories=getCategories(), form=form, vars=vars)

    return redirect(url_for('error'))

# Delete Product
@app.route("/product/delete", methods=['GET', 'POST'])
def adminDeleteProduct():
    if(request.method == "POST" and request.form.get('action') == 'delete'  and request.form.get('pid') != 0):
        pid = request.form.get('pid')
        # Get category by product id
        query = Products.query.filter_by(id=pid).first()
        cid  = query.category_id
        category = getCategories(*[cid])

        # Fetch and remove images from folder
        images = ProductsImages.query.filter_by(product_id=pid).all()
        for img in images : 
            os.remove(os.path.join(params['product_images_upload_path'] + category.lower() + '/', img.image_name))
            # Delete images from database
            deleteImages = ProductsImages.query.filter_by(product_id=pid).first()
            db.session.delete(deleteImages)
            db.session.commit()

        # # Delete product details from table
        product = Products.query.filter_by(id=pid).first()
        db.session.delete(product)
        db.session.commit()
        flash("Deleted Product! Successfully", "alert-danger")
        return redirect(url_for('adminProductPage', category=category.lower()))

    flash("Unexpected Error Occured", "alert-danger")
    return redirect(url_for('error'))


    # if(request.method == "POST" and request.form.get('action') == 'edit'  and request.form.get('fId') != ''):
    #     fId = request.form.get('fId')
    #     product = eval(cTable).query.filter_by(id=fId).first()

    #     fproduct_name = request.form.get('product_name')
    #     fproduct_desc = request.form.get('product_desc')
    #     fprice = request.form.get('price')
    #     fsku = request.form.get('sku')
    #     fdetails = request.form.get('product_details')

    #     product.product_name = fproduct_name,
    #     product.product_desc = fproduct_desc,
    #     product.price = fprice,
    #     product.sku = fsku,
    #     product.details = fdetails

    #     db.session.commit()

    #     # Upload product images
    #     if(request.files['productImg'].filename != ""):
    #         for f in request.files.getlist('productImg'):
    #             # create folder if doesn't exists
    #             f.save(os.path.join(params['product_images_upload_path'] + cTable.lower() + "/", secure_filename(f.filename)))
    #             insertImage = eval(iTable)(
    #                 image_name = f.filename,
    #                 product_id = fId
    #             )
    #             db.session.add(insertImage)
    #             db.session.commit()

    #     return redirect('/admin/' + cTable.lower() + '/')

# Invalid URL Error Handler
@app.errorhandler(404)
def page_not_found(e):
    render_template('auth/404.html', error=e), 404

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    render_template('500.html', error=e), 500
    
# Error Handling
@app.route("/error")
def error():
    return render_template('auth/error.html')
    
app.jinja_env.globals.update(getCategories=getCategories)
app.jinja_env.globals.update(NumberOfProducts=NumberOfProducts)

if __name__ == '__main__':
    app.run(debug=True)