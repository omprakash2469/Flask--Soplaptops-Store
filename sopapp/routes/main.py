# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, flash, redirect, url_for, session

# ----------- Application Modules ----------- #
from ..extensions import params, db
from ..functions import getCategories, returnMeta
from ..models.main import EmailForm, Emails, Categories, Products, ProductsImages, Contacts, ContactForm

# ----------- Instiantiate Blueprint ----------- #
main = Blueprint('main', __name__, template_folder='templates')

# ----------- Home Page ----------- #
@main.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    ### Add Email to database
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
    
    ### Trending Products
    products = {}
    i = 0
    for category in getCategories():
        c = category.category.lower()
        products[c] = {}
        fetchProduct = Products.query.filter_by(category_id=category.id).limit(2)
        for fp in fetchProduct:
            products[c][i] = {}
            image = ProductsImages.query.filter_by(product_id=fp.id).first()
            products[c][i]['product'] = fp.product
            products[c][i]['price'] = fp.price
            products[c][i]['image'] = image.image_name
            i+=1
        if products[c] == {}:
            products.pop(c)

    # SEO Meta data
    meta = returnMeta('home')
    return render_template('main/home.html', params=params, categories=getCategories(), form=form, products=products, meta=meta)

# ----------- Blogs Archives ----------- #
@main.route('/blogs')
def blogs():
    # SEO Meta data
    meta = returnMeta('blogs')
    return render_template('main/blogs.html', params=params, meta=meta, categories=getCategories())
    
# ----------- Products Archives ----------- #
@main.route('/category/<string:category>')
def productArchives(category):
    # Validate if category exists
    query = Categories.query.filter_by(category=category.lower()).first()
    if not query:
        flash("Category Doesn't exists")
        return render_template('404.html')

    # Get All Products
    allProducts = Products.query.filter_by(category_id=query.id).all()

    products = {}
    for i in allProducts:
        products[i.id] = {}
        image = ProductsImages.query.filter_by(product_id=i.id).first()
        products[i.id] = {
            "product": i.product,
            "product_url": url_for('main.singleProductPage', category=category.lower(), slug=i.product.replace(' ', '-').lower()),
            "price": i.price,
            "image": url_for('static', filename=f"assets/images/products/{category.lower()}/{image.image_name}")
        }
   
    # SEO Meta data
    meta = returnMeta('category')
    meta['title'] = category.capitalize() + " Laptops in Pune | " + params['blog_name']
    return render_template('main/shop.html', params=params, meta=meta, categories=getCategories(), category=category, products=products)

# ----------- Single Product Page ----------- #
@main.route("/category/<string:category>/<string:slug>")
def singleProductPage(category, slug):
    # Validate if category exists
    query = Categories.query.filter_by(category=category.lower()).first()
    if not query:
        flash("Category Doesn't exists")
        return render_template('404.html')

    ## Validate if product exists
    product_name = slug.replace('-', ' ').lower()
    products = Products.query.filter_by(product=product_name).first()
    if not products:
        flash("Product Not Found")
        return render_template('404.html')

    # Fetch product details
    category = category.capitalize()
    slug = slug.replace('-', ' ').lower()
    images = ProductsImages.query.filter_by(product_id=products.id).all()

    # Check if product is added in shopping cart
    button = ["false", "Add to Cart"]
    if 'shoppingCart' in session:
        for item in session['shoppingCart']:
            if int(products.id) == int(item):
                button = ["true", "Added to Cart"]
                break

    details = {
            "id": products.id,
            "product": products.product,
            "desc": products.product_desc,
            "price": products.price,
            "stock": products.stock,
            "details": products.details,
            "category": category.lower(),
            "urls": images,
            "button": button
    }

    # Fetch related product of current category
    related = Products.query.filter_by(category_id=products.category_id).limit(6)
    products = {}
    for i in related:
        products[i.id] = {}
        image = ProductsImages.query.filter_by(product_id=i.id).first()
        products[i.id] = {
            "product": i.product,
            "product_url": url_for('main.singleProductPage', category=category.lower(), slug=i.product.replace(' ', '-').lower()),
            "price": i.price,
            "image": url_for('static', filename=f"assets/images/products/{category.lower()}/{image.image_name}")
        }

        # Don't include current product in related product
        if i.id == details['id']:
            products.pop(i.id)

    # SEO Meta data
    meta = returnMeta('products')
    meta['title'] = slug.title() + f" | {category.upper()} | " + params['blog_name']
    return render_template('main/product.html', params=params, meta=meta, details=details, products=products, categories=getCategories())

# ----------- About ----------- #
@main.route("/about")
def about():

    # SEO Meta data
    meta = returnMeta('about')
    return render_template('main/about.html', params=params, categories=getCategories(), meta=meta)

# ----------- Privacy Policies ----------- #
@main.route("/privacy-policy")
def privacyPolicy():
    # SEO Meta data
    meta = returnMeta('privacy-policy')
    return render_template('main/privacy-policy.html', params=params, categories=getCategories(), meta=meta)

# ----------- Contact ----------- #
@main.route("/contact", methods = ['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Add Entry To Database
        fname = form.name.data
        femail = form.email.data
        flocation = form.location.data
        fsubject = form.subject.data
        fmessage = form.message.data

        # Enter Record
        try:
            entry = Contacts(name=fname, email=femail, location=flocation, subject=fsubject, message=fmessage)
            db.session.add(entry)
            db.session.commit()
            flash("Successfully Send! We will contact you soon", "text-green-500")
            return redirect(url_for('main.contact'))
        except:
            flash("Unexpected Error Occured", "text-red-600")
            return redirect(url_for('main.contact'))
    
    # SEO Meta data
    meta = returnMeta('contact')
    return render_template('main/contact.html', params=params, categories=getCategories(), form=form, meta=meta)


# ----------- Error Handling ----------- #
@main.route("/error")
def error():
    return render_template('error.html')