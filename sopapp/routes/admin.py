from itertools import count
from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename

from ..extensions import db
import os

from ..models.admin import LoginForm, AddCategory, AddProduct
from ..models.main import Categories, Products, ProductsImages
from ..extensions import params, getCategories

admin = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')

# ----------- Login and Dashboard ----------- #
@admin.route('/', methods=['GET', 'POST'])
def adminLogin():
    form = LoginForm()
    # Log in user
    if 'user' in session and session['loggedin']:
        return render_template('admin/index.html', params=params, categories=getCategories())

    # Validate submission
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if(username == params['admin'] and password == params['admin_password']):
            # Setting session variable
            session['user'] = username
            session['loggedin'] = True
            return redirect(url_for('admin.adminLogin'))

    return render_template('admin/login.html', params=params, form=form)

# ----------- Logout ----------- #
@admin.route('/logout/')
def adminLogout():
    session.pop('user',None)
    session.pop('loggedin',None)
    return redirect(url_for('admin.adminLogin'))

# ----------- Account ----------- #
@admin.route('/account/')
def adminAccount():
    return render_template('admin/account.html', params=params, categories=getCategories())

# ----------- Categories ----------- #
@admin.route("/categories", methods = ['GET', 'POST'])
#### Display Categories
def adminCategories():
    form = AddCategory()
    vars = {
        "title": "Add New Category",
        "action": url_for('admin.addCategories')
    }
    return render_template('admin/category.html',
        params=params,
        form=form,
        vars=vars,
        categories=getCategories()
    )

### Adding Categories
@admin.route("/categories/add", methods = ['GET', 'POST'])
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
        return redirect(url_for('admin.adminCategories'))
    else:
        flash("Try Again! Please Enter Required Details")
        return redirect(url_for('main.error'))

### Editing Categories
@admin.route("/categories/edit", methods = ['GET', 'POST'])
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
            # Upload Category Image
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
        return redirect(url_for('admin.adminCategories'))
    else:
        flash("Unexpected Error Occured", "alert-danger")
        return redirect(url_for('admin.adminCategories'))

### Deleting Categories
@admin.route("/categories/delete", methods = ['GET', 'POST'])
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
        return redirect(url_for('admin.adminCategories'))
    else:
        flash("Error Submitting Delete form")
        return redirect(url_for('main.error'))


# ----------- Products ----------- #
### Product Categories
@admin.route("/product")
def adminProducts():
    return render_template('admin/product-categories.html',params=params, categories=getCategories())

### Products Archives
@admin.route("/product/<string:category>")
def adminProductPage(category):
    try:
        query = Categories.query.filter_by(category=category.lower()).first()
        cid = query.id
    except Exception as e:
        flash('Category Not Exists', 'alert-danger')
        return redirect(url_for('main.error'))

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

### Add New Product
@admin.route("/product/add", methods=['GET', 'POST'])
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
            return redirect(url_for('main.error'))


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
        return redirect(url_for('admin.adminProductPage', category=category))
    vars = {
        "title": "Add New Product",
        "action": url_for('admin.adminAddProduct'),
        "product_name": "",
        "desc": "",
        "price": "",
        "stock": "",
        "details": "",
        "category": "",
        "button": "Submit"
    }

    return render_template('admin/add-product.html',params=params, categories=getCategories(), form=form, vars=vars)

### Edit Product Form
@admin.route("/product/editform", methods=['GET', 'POST'])
def adminEditProductForm():
    form = AddProduct()
    if request.method == "POST" and request.form.get('action') == 'editform' and request.form.get('pid'):
        pid = request.form.get('pid')
        query = Products.query.filter_by(id=pid).first()
        vars = {
        "title": "Update Product",
        "action": url_for('admin.adminEditProductForm'),
        "product_name": query.product,
        "desc": query.product_desc,
        "price": query.price,
        "stock": query.stock,
        "details": query.details,
        "category": query.category_id,
        "button": "Update"
        }
        return render_template('admin/add-product.html',params=params, categories=getCategories(), form=form, vars=vars)

    return redirect(url_for('main.error'))

### Edit Product
@admin.route("/product/edit", methods=['GET', 'POST'])
def adminEditProduct():
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

    return "Feature in Progress"

### Delete Product
@admin.route("/product/delete", methods=['GET', 'POST'])
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
        return redirect(url_for('admin.adminProductPage', category=category.lower()))

    flash("Unexpected Error Occured", "alert-danger")
    return redirect(url_for('main.error'))

# ----------- Context Processor ----------- #
@admin.context_processor
def context_processor():
    def NumberOfProducts(id):
        try:
            query = Products.query.filter_by(category_id=id).count()
            return query
        except:
            return False
    return dict(count=NumberOfProducts)