from flask import Flask, render_template, request, escape, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
import os
from os import listdir

with open('config.json', "r") as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_id'],
    MAIL_PASSWORD = params['gmail_password']
)
mail = Mail(app)
app.secret_key = 'hello-world'
app.config['SQLALCHEMY_DATABASE_URI'] = params['database_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(500), nullable=False)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    category_desc = db.Column(db.String(100), nullable=False)
    category_img = db.Column(db.String(50), nullable=False)
    product_image_table = db.Column(db.String(50), nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    street_nearby = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    customer = db.relationship('Customers', backref='orders', lazy=True)

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False) # foreign key for orders.id
    qty = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.Boolean(1), nullable=False)
    category_id = db.Column(db.String(20), nullable=False) 
    product_id = db.Column(db.Integer, nullable=False)

# Product Tables
class Apple(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class Lenovo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class Asus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class Hp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class Dell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class Apple_images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Asus_images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Dell_images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Lenovo_images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Hp_images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

# =========
# Functions
# =================================
def formatDetails(string):
    # Line Break
    text = string.replace('\n', '<br>')

    # Formatting the title
    text = text.replace('[', '<span class="format-bold-text">')
    text = text.replace(']', '</span>')
    # Formatting the content
    text = text.replace('{', '<span class="text-capitalize">')
    text = text.replace('}', '</span>')
    return text

def formatDesc(string):
    # Line Break
    text = string.replace('\n', '<br>')
    # Formatting the content
    text = text.replace('[', '<span class="text-capitalize">')
    text = text.replace(']', '</span>')
    return text


# =======
#  Front Endpoints 
# =================================
# Root
@app.route("/", methods = ['GET', 'POST'])
def root():
    # Add Email to database
    if(request.method=='POST'):
        femail = request.form.get('email')
        entry = Email(email=femail)
        db.session.add(entry)
        db.session.commit()
        return redirect('/#subscribe')

    # Trendy Products
    # Fetch all category names
    category = Categories.query.all()
    # Create product image table name
    products = {}
    for cat in category:
        imageTable = cat.category_name.capitalize() + "_images"
        # Fetch product details
        pFetch = eval(cat.category_name.capitalize()).query.limit(2)
        # Create product details dictionary
        products[cat.category_name] = {}
        k = 0
        for i in pFetch:
            k += 1
            products[cat.category_name][k] = {}
            # Fetch product images
            iFetch = eval(imageTable).query.filter_by(product_id=i.id).first()

            products[cat.category_name][k]['id'] = i.id
            products[cat.category_name][k]['name'] = i.product_name
            products[cat.category_name][k]['price'] = i.price
            products[cat.category_name][k]['image'] = iFetch.image_name


    firstCategories = Categories.query.limit(3)
    secondCategories = Categories.query.order_by(Categories.id.desc()).limit(2)
    secondCategories=secondCategories[::-1]

    return render_template('home.html', params=params, firstCategories=firstCategories, secondCategories=secondCategories, products=products)


# Product Archive pages
@app.route('/<string:category>', methods=['GET'])
def shop(category):
    category = category.capitalize()
    imageTable = category.capitalize() + "_images"

    # Fetch product details
    pFetch = eval(category).query.all()

    products = {}
    k = 0
    for i in pFetch:
        k += 1
        products[k] = {}
        iFetch = eval(imageTable).query.filter_by(product_id=i.id).first()

        products[k]['id'] = i.id
        products[k]['name'] = i.product_name
        products[k]['price'] = i.price
        products[k]['image'] = iFetch.image_name

    return render_template('shop.html', category=category.upper(), products=products, params=params)

# Single products
@app.route("/<string:category>/<string:slug>", methods=['GET'])
def single_products(category, slug):
    category = category.capitalize()
    imagesTable = category.capitalize() + "_images"
    # Fetch product details
    slug = slug.replace('-', ' ').lower()
    products = eval(category).query.filter_by(product_name=slug).first()
    images = eval(imagesTable).query.filter_by(product_id=products.id).all()
    details = {
            "id": products.id,
            "category": category.lower(),
            "product_name": products.product_name,
            "product_desc": products.product_desc,
            "price": products.price,
            "details": products.details,
            "urls": images
    }

    # Fetch related product details
    pFetch = eval(category).query.limit(5)
    rProducts = {}
    k = 0
    for i in pFetch:
        k += 1
        rProducts[k] = {}
        iFetch = eval(imagesTable).query.filter_by(product_id=i.id).first()

        rProducts[k]['id'] = i.id
        rProducts[k]['name'] = i.product_name
        rProducts[k]['price'] = i.price
        rProducts[k]['image'] = iFetch.image_name
    
    return render_template('product-single.html', params=params, details=details, rProducts=rProducts)

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

# # Cart
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
        return render_template('empty-cart.html', params=params)

    return render_template('cart.html', params=params)

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
        return render_template('confirmation.html', params=params, msg=True)
    else:
        msg = "Please Enter Delivery Details"
        return render_template('checkout.html', params=params, msg=msg)

# Gallery
galleryPath = params['gallery_images_folder']
@app.route("/gallery")
def gallery():
    images = os.listdir(galleryPath)
    return render_template('gallery.html', params=params, images=images)

# About
@app.route("/about")
def about():
    return render_template('about.html', params=params)

# Contact Us
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=="POST"):
        # Add entry to database
        fname = request.form.get('name')
        femail = request.form.get('email')
        flocation = request.form.get('location')
        fsubject = request.form.get('subject')
        fmessage = request.form.get('message')

        entry = Contact(name=fname, email=femail, location=flocation, subject=fsubject, message=fmessage)

        db.session.add(entry)
        db.session.commit()
        
        mail.send_message(fname,
        sender=femail.capitalize(),
        recipients= [params['gmail_id']],
        body = fmessage.capitalize() + "\n New Mail from : " + fname
        )

    return render_template('contact.html', params=params)


# ====== 
# Back Endpoints 
# ============================

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    # Log in user
    if('user' in session and session['user'] == params['admin']):
        return render_template('/admin/index.html', params=params)

    if(request.method == "POST"):
        username = request.form.get('username')
        userpass = request.form.get('password')
        if(username == params['admin'] and userpass == params['admin_password']):
            # Setting session variable
            session['user'] = username
            return redirect(request.referrer)

    return render_template('/admin/login.html', params=params)

# Logout Admin
@app.route('/admin/logout/')
def logout():
    session.pop('user',None)
    return redirect('/')

# Gallery
galleryPath = params['gallery_images_folder']
@app.route("/admin/gallery/")
def admin_gallery():
    # Upload Gallery Images
    if request.method == "POST" and request.files['catFile'].filename != "":
        for f in request.files.getlist('formFile'):
            f.save(os.path.join(params['gallery_images_folder'] + "/", secure_filename(f.filename)))

        return redirect(request.referrer)

    images = os.listdir(galleryPath)
    return render_template('/admin/gallery.html', params=params, images=images)

# Account Admin
@app.route('/admin/account/')
def account():
    return render_template('/admin/account.html', params=params)
    
# Adding Category
@app.route("/admin/categories/add", methods = ['GET', 'POST'])
def add_categories():
        # Adding New Category
    if(request.method=='POST' and request.form.get('action') == 'add'):
        fCategory = request.form.get('fCategory').lower()
        fDesc = request.form.get('fDesc')
        fProductImages = fCategory.strip().lower() + "_images"

        # Upload image file
        catImage = request.files['catFile']
        # -- Create image name
        fImageName = request.form.get('fImageName').strip().lower() + os.path.splitext(catImage.filename)[1]
        imageName = fImageName.strip().lower()
        imageName = imageName.replace(" ", "-")

        # -- Save Image file
        catImage.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName)))

        # Create Product Table

        # Create Product Images Table

        # Add record in Table
        entry = Categories(category_name=fCategory, category_desc=fDesc, category_img=imageName, product_image_table=fProductImages)
        
        db.session.add(entry)
        db.session.commit()
        return redirect('/admin/categories')
    
    return render_template('/admin/category-form.html',
    title="Add New Category",
    action='/admin/categories/add',
    submit_value='add',
    button='Add',
    categories = ('category_name', 'category_desc', 'category_img')
    )

# Editing and Deleting Category
@app.route("/admin/categories", methods = ['GET', 'POST'])
def edit_categories():
    if(request.method=='POST' and request.form.get('action') == 'editform' and request.form.get('fId') != ""):
        fId = request.form.get('fId')
        categories = Categories.query.filter_by(id=fId).first()

        return render_template('/admin/category-form.html',
            params=params,
            title="Update Category",
            categories=categories,
            action='/admin/categories',
            submit_value='edit',
            button='Update'
        )

    # Edit Category
    if(request.method=='POST' and request.form.get('action') == 'edit'):
        fId = request.form.get('fId')
        fCategory = request.form.get('fCategory').lower()
        fDesc = request.form.get('fDesc')
        fProductImages = fCategory.strip().lower() + "_images"

        # Fetched Record
        fetchedRecord = Categories.query.filter_by(id=fId).first()
        imageName = fetchedRecord.category_img
        # If file is uploaded then delete old image
        if(request.files['catFile'].filename != ""):
            # Fetch category image name by category id
            # Delete old Image from categories folder
            os.remove(os.path.join(params['category_images_upload_path'], imageName))
            # Upload new image file
            catImage = request.files['catFile']
            # -- Create image name
            fImageName = request.form.get('fImageName').strip().lower() + os.path.splitext(catImage.filename)[1]
            imageName = fImageName.strip().lower()
            imageName = imageName.replace(" ", "-")
            # -- Save Image file
            catImage.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName)))

        
        # Update Product Table Name

        # Update Product Images Table Name

        # Add record in table
        fetchedRecord.category_name = fCategory,
        fetchedRecord.category_desc = fDesc,
        fetchedRecord.category_img = imageName,
        fetchedRecord.product_image_table = fProductImages
        db.session.commit()
        return redirect('/admin/categories')

    # Delete Categories
    if(request.method=='POST' and request.form.get('action') == 'delete' and request.form.get('fId') != ""):
        fId = request.form.get('fId')
        categories = Categories.query.filter_by(id=fId).first()
        os.remove(os.path.join(params['category_images_upload_path'], categories.category_img))
        db.session.delete(categories)
        db.session.commit()
        return redirect('/admin/categories')

    categories = Categories.query.all()
    return render_template('/admin/category.html', params=params, categories=categories)

# Display product adding form
@app.route("/admin/<string:category>/add", methods=['GET'])
def add_product_form(category):
    return render_template('/admin/product-form.html',
            title= category.capitalize() + " - Add Product",
            category = category,
            product= '',
            images = '',
            action='/admin/' + category.lower(),
            submit_value='add',
            button='Add'
        )


# Adding Product Details
@app.route("/admin/<string:category>/", methods=['GET', 'POST'])
def admin_products(category):
    cTable = category.capitalize()
    iTable = category.capitalize() + "_images"
    if(request.method == "POST" and request.form.get('action') == 'add'):
        # Check image upload 
        if(request.files['productImg'].filename == ""):
            return render_template('/admin/product-form.html',
            title= cTable + " - Add Product",
            category = cTable,
            product= '',
            images = '',
            msg = 'Please Upload Image files',
            action='/admin/' + cTable.lower(),
            submit_value='add',
            button='Add'
        )
        # Get form values
        fproduct_name = request.form.get('product_name')
        fproduct_desc = request.form.get('product_desc')
        fprice = request.form.get('price')
        fsku = request.form.get('sku')
        fdetails = request.form.get('product_details')

        entry = eval(cTable)(
            product_name = fproduct_name,
            product_desc = fproduct_desc,
            price = fprice,
            sku = fsku,
            details = fdetails
        )
        db.session.add(entry)
        db.session.commit()
        db.session.flush()
        lastInsertedId = entry.id

        # Upload product images
        for f in request.files.getlist('productImg'):
            # create folder if doesn't exists
            if (os.path.isdir(params['product_images_upload_path'] + cTable.lower() + '/') == False):
                os.makedirs(params['product_images_upload_path'] + cTable.lower() + '/', exist_ok=True)

            f.save(os.path.join(params['product_images_upload_path'] + cTable.lower() + "/", secure_filename(f.filename)))
            insertImage = eval(iTable)(
                image_name = f.filename,
                product_id = lastInsertedId
            )
            db.session.add(insertImage)
            db.session.commit()

        return redirect('/admin/' + cTable.lower() + '/')

    if(request.method == "POST" and request.form.get('action') == 'editform' and request.form.get('fId') != ''):
        fId = request.form.get('fId')
        product = eval(cTable).query.filter_by(id=fId).first()
        productImages = eval(iTable).query.filter_by(product_id=fId).all()
        return render_template('/admin/product-form.html',
            title= cTable + " - Update Product",
            category= cTable,
            product= product,
            images = productImages,
            action='/admin/' + cTable.lower(),
            submit_value='edit',
            button='Update'
        )

    if(request.method == "POST" and request.form.get('action') == 'edit'  and request.form.get('fId') != ''):
        fId = request.form.get('fId')
        product = eval(cTable).query.filter_by(id=fId).first()

        fproduct_name = request.form.get('product_name')
        fproduct_desc = request.form.get('product_desc')
        fprice = request.form.get('price')
        fsku = request.form.get('sku')
        fdetails = request.form.get('product_details')

        product.product_name = fproduct_name,
        product.product_desc = fproduct_desc,
        product.price = fprice,
        product.sku = fsku,
        product.details = fdetails

        db.session.commit()

        # Upload product images
        if(request.files['productImg'].filename != ""):
            for f in request.files.getlist('productImg'):
                # create folder if doesn't exists
                f.save(os.path.join(params['product_images_upload_path'] + cTable.lower() + "/", secure_filename(f.filename)))
                insertImage = eval(iTable)(
                    image_name = f.filename,
                    product_id = fId
                )
                db.session.add(insertImage)
                db.session.commit()

        return redirect('/admin/' + cTable.lower() + '/')

    if(request.method == "POST" and request.form.get('action') == 'delete'  and request.form.get('fId') != ''):
        fId = request.form.get('fId')
        # Fetch and remove images from folder
        
        images = eval(iTable).query.filter_by(product_id=fId).all()
        for img in images : 
            os.remove(os.path.join(params['product_images_upload_path'] + cTable.lower() + '/', img.image_name))
            # delete images from database
            deleteImages = eval(iTable).query.filter_by(product_id=fId).first()
            db.session.delete(deleteImages)
            db.session.commit()


        # # Delete product details from table
        product = eval(cTable).query.filter_by(id=fId).first()
        db.session.delete(product)
        db.session.commit()
        return redirect('/admin/' + cTable.lower() + '/')

    products = eval(cTable).query.all()
    return render_template('/admin/product.html', category=cTable, products=products)

@app.route("/admin/<string:category>/remove", methods=['GET', 'POST'])
def remove_product_image(category):
    iTable = category.capitalize() + "_images"
    if request.method == "POST" and request.form.get('imageId'):
        id = request.form.get('imageId')
        # fetch image name using id
        image = eval(iTable).query.filter_by(id=id).first()
        
        os.remove(os.path.join(params['product_images_upload_path'] + category.lower() + "\\", image.image_name))
        # delete image from database
        db.session.delete(image)
        db.session.commit()
        return redirect('/admin/' + category.lower() + '/')

app.jinja_env.globals.update(formatDetails=formatDetails)
app.jinja_env.globals.update(formatDesc=formatDesc)
app.run(debug=True)