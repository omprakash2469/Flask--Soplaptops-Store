from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.exceptions import BadRequest
from ..extensions import params, getCategories, db
from ..models.main import EmailForm, Emails, Categories, Products, ProductsImages

main = Blueprint('main', __name__, template_folder='templates')

# ----------- Home Page ----------- #
@main.route('/')
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

    return render_template('main/home.html', params=params, categories=getCategories(), form=form )

# ----------- Products Archives ----------- #
@main.route('/products/<string:category>')
def productArchives(category):
    # Validate if category exists
    try:
        query = Categories.query.filter_by(category=category.lower()).first()
        if query:
            cid = query.id
    except Exception as e:
        flash("Unexpected Error Occured")
        return redirect(url_for('main.error'))

    # Get Products
    try:
        query = Products.query.filter_by(category_id=cid).all()
    except:
        flash("Products Not Found")
        return redirect(url_for('main.error'))

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

    return render_template('main/shop.html', params=params, categories=getCategories(), category=category, products=products)

# ----------- Single Product Page ----------- #
@main.route("/products/<string:category>/<string:slug>")
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
        return redirect(url_for('main.error'))

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
    
    return render_template('main/product.html', params=params, details=details, rProducts=rProducts, categories=getCategories())

# ----------- About ----------- #
@main.route("/about")
def about():
    return render_template('main/about.html', params=params, categories=getCategories())

# ----------- Privacy Policies ----------- #
@main.route("/privacy-policy")
def privacyPolicy():
    return "Updating our policies soon"

# ----------- Contact ----------- #
@main.route("/contact", methods = ['GET', 'POST'])
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
                return redirect(url_for('main.contact'))
            except:
                flash("Unexpected Error Occured", "text-red-600")
                return redirect(url_for('main.contact'))
        else:
            flash("Please Enter Details", "text-red-600")
            return redirect(url_for('main.contact'))

    return render_template('main/contact.html', params=params, categories=getCategories())


# ----------- Error Handling ----------- #
@main.route("/error")
def error():
    return render_template('error.html')