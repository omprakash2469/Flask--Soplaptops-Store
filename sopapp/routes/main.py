# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, flash, redirect, url_for, session, send_from_directory, request

# ----------- Application Modules ----------- #
from ..extensions import ROOT_DIR, db, params
from ..functions import getCategories, adminById
from ..models.main import EmailForm, Emails, Categories, Products, Contacts, ContactForm, Blogs
from ..seo import meta, brand_name, primary_keyword

# ----------- Instiantiate Blueprint ----------- #
main = Blueprint('main', __name__, template_folder='templates')

# ----------- Sitemap ----------- #
@main.route('/robots.txt')
@main.route('/sitemap.xml')
def sitemap():
    path = ROOT_DIR + "/static"
    return send_from_directory(path, request.path[1:])

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
    for category in getCategories():
        c = category.category.lower()
        fetchProduct = Products.query.filter_by(category_id=category.id).limit(2)
        i = 0
        products[c] = {}
        for p in fetchProduct:
            products[c][i] = p
            i+=1

    # Blogs
    blogs = Blogs.query.order_by(Blogs.views.desc()).limit(4)

    # SEO Meta data
    head = meta['home']
    head['canonical'] = request.base_url
    return render_template('main/home.html', head=head, form=form, categories=getCategories(), products=products, blogs=blogs)

# ----------- Blogs Archives ----------- #
@main.route('/blogs')
def blogs():
    # SEO Meta data
    head = meta['blogs']
    head['canonical'] = request.base_url
    return render_template('main/blogs.html', head=head, categories=getCategories(), blogs=Blogs.query.all())

# ----------- Single Blog Page ----------- #
@main.route('/blog/<string:slug>')
def single_blog(slug):
    slug = slug.lower()
    ## Validate if blogs exists
    blog = Blogs.query.filter(Blogs.slug.ilike(slug)).first()
    
    if not blog:
        flash("Page Not Found")
        return render_template('404.html')

    # Update Views
    blog.views += 1
    db.session.commit()

    blog.admin_id = adminById(blog.admin_id)

    # Get Related Blogs
    relatedBlog = Blogs.query.filter(Blogs.id!=blog.id).limit(2)

    # SEO Meta data
    head = meta['single_blog']
    head['title'] = blog.title + f" || {brand_name}"
    head['desc'] = blog.metaDesc
    head['canonical'] = request.base_url
    return render_template('main/single-blog.html', head=head, categories=getCategories(), blog=blog, relatedBlog=relatedBlog)
    
# ----------- Products Archives ----------- #
@main.route('/category/<string:category>')
def productArchives(category):
    # Validate if category exists
    query = Categories.query.filter_by(category=category.lower()).first()
    if not query:
        flash("Category Doesn't exists")
        return render_template('404.html')

    # Get All Products
    products = Products.query.filter_by(category_id=query.id).all()
   
    # SEO Meta data
    head = meta['category']
    head['title'] = query.category.capitalize() + f" | {brand_name} | {primary_keyword}"
    head['desc'] = f"Best deals on {query.category} Computers and Laptops in Pune. Explore products and Buy Now"
    head['canonical'] = request.base_url
    return render_template('main/shop.html', head=head, categories=getCategories(), category=category.lower(), products=products)

# ----------- Single Product Page ----------- #
@main.route("/category/<string:category>/<string:slug>")
def singleProductPage(category, slug):
    # Validate if category exists
    query = Categories.query.filter_by(category=category.lower()).first()
    if not query:
        flash("Category Doesn't exists")
        return render_template('404.html')

    ## Validate if product exists
    slug = slug.lower()
    product = Products.query.filter_by(slug=slug).first()
    if not product:
        flash("Product Not Found")
        return render_template('404.html')

    # Check if product is added in shopping cart
    button = ["false", "Add to Cart"]
    if 'shoppingCart' in session:
        for item in session['shoppingCart']:
            if int(product.id) == int(item):
                button = ["true", "Added to Cart"]
                break

    # Fetch related product of current category
    relatedProducts = Products.query.filter(Products.id!=product.id, Products.category_id==product.category_id).limit(6)

    # SEO Meta data
    head = meta['product']
    head['title'] = product.product + f" | {brand_name}"
    head['desc'] = product.product_desc
    head['canonical'] = request.base_url
    return render_template('main/product.html', head=head, categories=getCategories(), product=product, relatedProducts=relatedProducts, category=category, button=button)

# ----------- About ----------- #
@main.route("/about")
def about():

    # SEO Meta data
    head = meta['about']
    head['canonical'] = request.base_url
    return render_template('main/about.html', categories=getCategories(), head=head)

# ----------- Privacy Policies ----------- #
@main.route("/privacy-policy")
def privacyPolicy():
    # SEO Meta data
    head = meta['privacy-policy']
    head['canonical'] = request.base_url
    return render_template('main/privacy-policy.html', categories=getCategories(), head=head)

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
    head = meta['contact']
    head['canonical'] = request.base_url
    return render_template('main/contact.html', categories=getCategories(), form=form, head=head)


# ----------- Error Handling ----------- #
@main.route("/error")
def error():
    return render_template('error.html')