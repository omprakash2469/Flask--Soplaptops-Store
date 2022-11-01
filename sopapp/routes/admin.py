# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
import os

# ----------- Application Modules ----------- #
from ..models.admin import AddCategory, AddProduct
from ..models.main import Categories, Contacts, Products, ProductsImages
from ..models.users import Users, Orders
from ..extensions import ROOT_DIR, db, params
from ..functions import authAdminRole, getCategories

# ----------- Instiantiate Blueprint ----------- #
admin = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')


# ----------- Categories ----------- #
#### Display Categories
@admin.route("/categories", methods = ['GET', 'POST'])
@login_required
def adminCategories():
    form = AddCategory()
    vars = {
        "title": "Add New Category",
        "action": url_for('admin.addCategories')
    }
    return render_template('admin/category.html',
        form=form,
        vars=vars,
        categories=getCategories()
    )

#### Adding Categories
@admin.route("/categories/add", methods = ['GET', 'POST'])
@login_required
def addCategories():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminCategories'))

    ### Check if User Has Role
    form = AddCategory()
    if form.validate_on_submit():
        ## Adding New Category
        category = form.category.data
        tagline = form.tagline.data
        imgname = form.image.data
        imagefile = form.image_file.data

        ## Create Image filename
        imageName = imgname.strip().lower().replace(' ', '-') + os.path.splitext(imagefile.filename)[1]
        # Check if category folder exists
        if not os.path.exists(params['category_images_upload_path']):
            os.mkdir(params['category_images_upload_path'])

        ## Save Image file
        imagefile.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName)))
        ## Add record in Table
        entry = Categories(category=category.lower(), tagline=tagline, category_img=secure_filename(imageName))
        db.session.add(entry)
        db.session.commit()
        flash("Successfully! Added Category", "alert-success")
        return redirect(url_for('admin.adminCategories'))
    else:
        ## Return Error if information is not returned
        flash("Try Again! Please Enter Required Details")
        return redirect(url_for('main.error'))

#### Editing Categories
@admin.route("/categories/edit", methods = ['GET', 'POST'])
@login_required
def editCategories():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminCategories'))

    form = AddCategory()
    if form.validate_on_submit():
        ### Update Category
        cid = form.cid.data
        category = form.category.data
        tagline = form.tagline.data
        imgname = form.image.data
        imagefile = form.image_file.data
        data = Categories.query.filter_by(id=cid).first()

       ### Check if Image is uploaded
        if imagefile != None:
            ## Create Image filename
            imageName = imgname.strip().lower().replace(' ', '-') + os.path.splitext(imagefile.filename)[1]
            oldImageName = data.category_img
            ## Check if file exists
            imagePath = params['category_images_upload_path']+ oldImageName
            if os.path.exists(imagePath):
                os.remove(imagePath) # Remove old image
            ## Upload Category Image
            imagefile.save(os.path.join(params['category_images_upload_path'], secure_filename(imageName))) # Upload New Image
        else:
            ## Create Image filename
            ext = os.path.splitext(data.category_img)[1]
            imageName = imgname.strip().lower().replace(' ', '-') + ext
            src = params['category_images_upload_path'] + data.category_img
            dest = params['category_images_upload_path'] + imageName
            os.rename(src, dest)
 
        ### Update record in Table
        data.category = category
        data.tagline = tagline
        data.category_img = imageName
        db.session.commit()
        flash("Successfully! Updated Category", "alert-success")
        return redirect(url_for('admin.adminCategories'))
    else:
        ### Return Error if form not filled
        flash("Unexpected Error Occured", "alert-danger")
        return redirect(url_for('admin.adminCategories'))

#### Deleting Categories
@admin.route("/categories/delete", methods = ['GET', 'POST'])
@login_required
def deleteCategories():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminCategories'))

    ### Delete Categories
    if request.method == "POST" and request.form.get('cid')!='':
        cid = request.form.get('cid')
        categories = Categories.query.filter_by(id=cid).first()
        ## Delete Category Image
        imagepath = os.path.join(params['category_images_upload_path'], categories.category_img)
        if os.path.exists(imagepath):
            os.remove(imagepath)
        ## Delete category from table
        db.session.delete(categories)
        db.session.commit()
        flash('Deleted Successfully', 'alert-danger')
        return redirect(url_for('admin.adminCategories'))
    else:
        ## Return Error if unable to delete category
        flash("Error Submitting Delete form")
        return redirect(url_for('main.error'))


# ----------- Products ----------- #
#### Display Product Categories
@admin.route("/product")
@login_required
def adminProducts():
    return render_template('admin/product-categories.html', categories=getCategories())

#### Products Archives Page
@admin.route("/product/<string:category>")
@login_required
def adminProductPage(category):
    try:
        query = Categories.query.filter_by(category=category.lower()).first()
        cid = query.id
    except Exception as e:
        flash('Category Not Exists', 'alert-danger')
        return redirect(url_for('main.error'))

    ### Fetch all products in a category
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

    return render_template('admin/product.html', categories=getCategories(), category=query.category, products=products)

#### Add New Product
@admin.route("/product/add", methods=['GET', 'POST'])
@login_required
def adminAddProduct():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'content editor'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminProducts'))

    form = AddProduct()
    form.category.choices = [(c.id, c.category) for c in getCategories()]
    if form.validate_on_submit():
        ### Get form values
        fproduct_name = form.product_name.data
        fdesc = form.desc.data
        fprice = form.price.data
        fstock = form.stock.data
        fdetails = form.details.data
        fcategory = form.category.data
        fimage_file = form.image_file.data

        ### Check if Images are Uploaded
        if fimage_file[0]:
            ## Insert product info into database
            entry = Products(product = fproduct_name.lower(), product_desc = fdesc, price = fprice, stock = fstock, details = fdetails, category_id = fcategory)
            db.session.add(entry)
            db.session.commit()
            db.session.flush()
            pid = entry.id

            # Check if products folder exists
            if not os.path.exists(params['product_images_upload_path']):
                os.mkdir(params['product_images_upload_path'])

            ## Upload product images
            category = getCategories(fcategory)
            for img in fimage_file:

                # create folder if doesn't exists
                if (os.path.isdir(params['product_images_upload_path'] + category + '/') == False):
                    os.makedirs(params['product_images_upload_path'] + category + '/', exist_ok=True)
                image = secure_filename(str(pid) + "_" + img.filename)
                img.save(os.path.join(params['product_images_upload_path'] + category + "/", image))
                insertImage = ProductsImages(
                    image_name = image,
                    product_id = pid
                )
                db.session.add(insertImage)
                db.session.commit()
            flash("Successfully! Added New Product", "alert-success")
            return redirect(url_for('admin.adminProductPage', category=category))
        else:
            flash("Please Upload Images", "alert-danger")
            return redirect(request.referrer)

    ### Set Form Values
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

    return render_template('admin/add-product.html', categories=getCategories(), form=form, vars=vars)

#### Edit Product
@admin.route("/product/editform", methods=['GET', 'POST'])
@login_required
def adminEditProductForm():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'content editor'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminProducts'))

    form = AddProduct()
    form.category.choices = [(c.id, c.category) for c in getCategories()]
    ### Display Product Edit Form
    if request.method == "POST" and request.form.get('action') == 'editform' and request.form.get('pid'):
        pid = request.form.get('pid')
        query = Products.query.filter_by(id=pid).first()
        form.desc.data = query.product_desc # Populate textarea field
        form.details.data = query.details # Populate ckeditor field
        ## Note = Textarea cannot be populated through below mentioned format. That's why you have to do it like form.desc.data = value
        ## Note = Ckeditor field cannot be populated through below mentioned format. That's why you have to do it like form.details.data = value
        vars = {
        "title": "Update Product",
        "action": url_for('admin.adminEditProductForm'),
        "product_name": query.product,
        "price": query.price,
        "stock": query.stock,
        "category": query.category_id,
        "images": ProductsImages.query.filter_by(product_id=query.id).all(),
        "button": "Update"
        }
        return render_template('admin/add-product.html', categories=getCategories(), form=form, vars=vars)
    
    ### Edit Product Information
    if  form.validate_on_submit() and request.form.get('pid'):
        ## Get Product Id
        pid = request.form.get('pid')
        ## Get form values
        fproduct_name = form.product_name.data
        fdesc = form.desc.data
        fprice = form.price.data
        fstock = form.stock.data
        fdetails = form.details.data
        fcategory = form.category.data
        fimage_file = form.image_file.data
        ## Get category by id
        category = getCategories(fcategory)

        ## Delete Old Product
        try:
            # Delete old product entry
            query = Products.query.filter_by(id=pid).first()
            db.session.delete(query)
            db.session.commit()
        except Exception as e:
            flash("Refresh and Try Again! Unable to Delete Product", "alert-danger")
            return redirect(url_for('admin.adminProductPage', category=category))

        ## Insert new product info into database
        entry = Products(product = fproduct_name.lower(), product_desc = fdesc, price = fprice, stock = fstock, details = fdetails, category_id = fcategory)
        db.session.add(entry)
        db.session.commit()
        db.session.flush()
        newPid = entry.id

        ## Update old product images
        oldImages = ProductsImages.query.filter_by(product_id=pid).all()
        for img in oldImages:
            img.product_id = newPid
            db.session.commit()

        ## Upload product images
        if fimage_file[0]:
            for img in fimage_file:
                image = secure_filename(img.filename)
                img.save(os.path.join(params['product_images_upload_path'] + category + "/", image))
                insertImage = ProductsImages(
                    image_name = image,
                    product_id = newPid
                )
                db.session.add(insertImage)
                db.session.commit()
        flash("Successfully! Update Product", "alert-success")
        return redirect(url_for('admin.adminProductPage', category=category))
    
    flash("Unexpected Error Occured, while updating product", "alert-danger")
    return redirect(request.referrer)

#### Delete Product
@admin.route("/product/delete", methods=['GET', 'POST'])
@login_required
def adminDeleteProduct():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'content editor'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('admin.adminProducts'))

    ### Validate if required values are set
    if(request.method == "POST" and request.form.get('action') == 'delete'  and request.form.get('pid')):
        pid = request.form.get('pid')
        ### Get category by product id
        query = Products.query.filter_by(id=pid).first()
        cid  = query.category_id
        category = getCategories(*[cid])

        ### Fetch and remove images from folder
        try:
            images = ProductsImages.query.filter_by(product_id=pid).all()
            for img in images : 
                os.remove(os.path.join(params['product_images_upload_path'] + category + '/', img.image_name))
                ## Delete images from database
                db.session.delete(img)
                db.session.commit()
        except Exception as e:
            flash("Unable to delete images", "alert-danger")

        ### Delete product details from table
        try:
            product = Products.query.filter_by(id=pid).first()
            db.session.delete(product)
            db.session.commit()
            flash("Deleted Product! Successfully", "alert-danger")
            return redirect(url_for('admin.adminProductPage', category=category))
        except Exception as e:
            flash("Error Deleting Product!", "alert-danger")
            return redirect(url_for('admin.adminProductPage', category=category))

    flash("Unexpected Error Occured", "alert-danger")
    return redirect(url_for('admin.adminProductPage', category=category))
    
# ----------- Settings ----------- #
#### Display Settings
@admin.route("/settings")
@login_required
def adminSettings():
    return render_template('error.html')
    
# ----------- Orders ----------- #
#### Display Orders
@admin.route("/orders")
@login_required
def adminOrders():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return render_template('404.html')
    fetchOrders = Orders.query.all()
    orders = {}
    for fo in fetchOrders:
        orders[fo.id] = {}
        # Get Details
        username = Users.query.filter_by(id=fo.user_id).first() ## Get username by id
        product = Products.query.filter_by(id=fo.product_id).first() ## Get products by id
        if fo.status == 0:
            status = "bg-red-300"
        else: 
            status = "bg-green-300"

        orders[fo.id] = {
            "username": username.name.capitalize(),
            "product": product.product,
            "price": product.price * fo.quantity,
            "quantity": fo.quantity,
            "doo": fo.order_date,
            "status": status
        }

    return render_template('admin/orders.html', orders=orders)

# ----------- Users ----------- #
#### Display Users
@admin.route("/users")
@login_required
def adminUsers():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return render_template('404.html')

    users = Users.query.all()
    return render_template('admin/users.html', users=users)
    
# ----------- Contact Us ----------- #
#### Display Contacts
@admin.route("/contact", methods=['GET', 'POST'])
@login_required
def adminContact():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return render_template('404.html')
    
    ### Delete User
    if request.method == "POST" and request.form.get("userid"):
        id = request.form.get("userid")
        query = Contacts.query.filter_by(id=id).first()
        db.session.delete(query)
        db.session.commit()
        flash("Deleted Contacted User", "alert-danger")
        return redirect(url_for('admin.adminContact'))

    contacts = Contacts.query.all()
    return render_template('admin/contact.html', contacts=contacts)
    
# ----------- Tools ----------- #
@admin.route("/tools", methods=['GET', 'POST'])
@login_required
def adminTools():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'site admin'):
        flash('This page is not accessible', "alert-danger")
        return render_template('404.html')
    
    if request.method == "POST":
        ### Upload Sitemap.xml file
        if request.form.get('action') == 'sitemap':
            file = request.files['sitemap']
            if file.filename != 'sitemap.xml':
                flash('Please upload sitemap.xml file only', "alert-danger")
                return redirect(url_for('admin.adminTools'))

            ## Save sitemap.xml file
            path = ROOT_DIR + "/static/sitemap.xml"
            if os.path.exists(path):
                os.remove(path)
            file.save(path)
            flash('Successfully! Uploaded sitemap', "alert-success")
            return redirect(url_for('admin.adminTools'))
        ### Upload Robots.txt file
        elif request.form.get('action') == 'robots':
            file = request.files['robots']
            if file.filename != 'robots.txt':
                flash('Please upload robots.txt file only', "alert-danger")
                return redirect(url_for('admin.adminTools'))

            ## Save srobots.txt file
            path = ROOT_DIR + "/static/robots.txt"
            if os.path.exists(path):
                os.remove(path)
            file.save(path)
            flash('Successfully! Uploaded Robots.txt', "alert-success")
            return redirect(url_for('admin.adminTools'))
        else:
            flash('Unexpected Error Occured', "alert-danger")
            return redirect(url_for('admin.adminTools'))

    return render_template('admin/tools.html')