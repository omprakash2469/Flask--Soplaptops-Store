# ----------- Flask Modules ----------- #
from ast import Param
from flask import Blueprint, render_template, request, flash, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

# ----------- Application Modules ----------- #
from ..models.users import Orders, OrdersForm, Users, UserRegisterForm, UserUpdateForm
from ..models.main import Products, ProductsImages
from ..models.auth import LoginForm
from ..extensions import db, params
from ..functions import MergeDicts, getCategories, getCategoryById, returnMeta

# ----------- Instiantiate Blueprint ----------- #
users = Blueprint('users', __name__, template_folder='templates')

# ----------- User Dashboard ----------- #
@users.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # Redirect User if not logged in
    if not 'user_logged_in' in session and not 'username' in session:
        flash("Please login to continue", "text-red-500")
        return redirect(url_for('users.login'))
    
    ### User information update form
    form = UserUpdateForm()
    if form.validate_on_submit():
        name = form.name.data
        number = form.number.data
        email = form.email.data
        address = form.address.data
        street = form.street.data
        zipcode = form.zipcode.data

        ## Update user in database
        query = Users.query.filter_by(id=session['id']).first()
        if query:
            # Validate and check for duplicate entry of email
            if query.email != email:
                emailExist = Users.query.filter_by(email=email).first()
                if emailExist:
                    flash("Email Already Exists! Please Login", "text-red-500")
                    return redirect(url_for('users.dashboard'))
                else:
                    query.email = email
            query.name = name
            query.number = number
            query.address = address
            query.street = street
            query.zipcode = zipcode
            db.session.commit()
                    
            ## Update session values
            session['username'] = name
        
            flash("Successfully! Updated your information", "text-green-500")
            return redirect(url_for('users.dashboard'))

    ### Get current loggedin's user orders
    orders = {}
    userOrders = Orders.query.filter_by(user_id=session['id']).all()
    for order in userOrders:
        ## Get Product Information by product id
        product = Products.query.filter_by(id=order.product_id).first()
        category = getCategoryById(product.category_id) # Get category of product
        image = ProductsImages.query.filter_by(product_id=product.id).first()
        url = url_for('static', filename=f"assets/images/products/{category}/{image.image_name}") # Get product image
        ## Add Product to Cart
        item = {
            order.id : {
                'pid': product.id,
                'category': category,
                'name': product.product,
                'product_url': url_for('main.singleProductPage', category=category, slug=product.product.replace(' ', '-').lower()),
                'price': int(product.price) * int(order.quantity),
                'order_date': order.order_date.strftime("%d/%m/%Y"),
                'quantity': int(order.quantity),
                'image': url
            }
        }
        orders.update(item)

    
    ### Get User Details of current logged in user
    currentUser = Users.query.filter_by(id=session['id']).first() ## Get loggedin user
    user = {
        'name': session['username'].capitalize(),
        "number": currentUser.number,
        "email": currentUser.email,
        "address": currentUser.address.capitalize(),
        "street": currentUser.street,
        "zipcode": currentUser.zipcode
    }

    # SEO Meta data
    meta = returnMeta('user')
    meta['title'] = session['username'] + " || Dashboard - " + params['blog_name']
    return render_template('users/index.html', meta=meta, categories=getCategories(), orders=orders, user=user, form=form, uo=userOrders)


# ----------- Shopping Cart ----------- #
### Add Product to cart and Display Cart
@users.route("/cart", methods=['GET', 'POST'])
def userCart():
    if request.method == "POST":
        data = request.get_json()
        pid = data['pid']
        quantity = data['quantity']
        
        ## Validate required values
        if pid and quantity:
            ## Get Product Information by product id
            product = Products.query.filter_by(id=pid).first()
            category = getCategoryById(product.category_id) # Get category of product
            image = ProductsImages.query.filter_by(product_id=pid).first()
            url = url_for('static', filename=f"assets/images/products/{category}/{image.image_name}") # Get product image

            ## Add Product to Cart
            cartItems = {
                pid : {
                    'category': category,
                    'name': product.product,
                    'product_url': url_for('main.singleProductPage', category=category, slug=product.product.replace(' ', '-').lower()),
                    'price': int(product.price) * int(quantity),
                    'quantity': int(quantity),
                    'image': url
                }
            }

            ## Check if cart session is started
            if 'shoppingCart' in session:
                ## Check if product exists in cart
                if pid in session['shoppingCart']:
                    return {"state": "bg-red-200", "message":"Product Already Added in cart"}

                ## Add product in cart if not exits
                session['shoppingCart'] = MergeDicts(session['shoppingCart'], cartItems)
                return {"state": "bg-green-200", "message":"Added Your Product in Cart"}
            else:
                session['shoppingCart'] = cartItems
                return {"state": "bg-green-200", "message":"Added Your Product in Cart"}
        else:
            return {"state": "bg-red-200", "message":"Refresh! And Try Again"}


    return redirect(url_for('main.index'))

### Remove Cart Item
@users.route("/removeitem", methods=['GET', 'POST'])
def removeCartItem():
    if request.method == "POST":
        data = request.get_json()
        pid = data['value']
        session['shoppingCart'].pop(pid, None)
        session.modified = True
        return {"state": "bg-green-200", "message":"Removed Cart Item!"}
    else:
        return {"state": "bg-red-200", "message":"Refresh! And Try Again"}

# ----------- Checkout ----------- #
@users.route("/checkout", methods=['GET', 'POST'])
def checkout():
    # Check if product are there in cart
    if 'shoppingCart' not in session:
        return redirect(url_for('main.index'))

    if 'id' not in session and 'username' not in session and 'user_logged_in' not in session:
        flash("Please Login To Proceed to Checkout", "text-red-500")
        return redirect(url_for('users.login'))

    # Get Current User info
    loggedinUser = Users.query.filter_by(id=session['id']).first()

    form = OrdersForm()
    if form.validate_on_submit():
        fname = form.name.data
        fnumber = form.number.data
        fstreet = form.street.data
        faddress = form.address.data
        fzipcode = form.zipcode.data

        ## User Authentication
        # Update user street, address and zipcode
        try:
            loggedinUser.name = fname,
            loggedinUser.number = fnumber,
            loggedinUser.street = fstreet,
            loggedinUser.address = faddress,
            loggedinUser.zipcode = fzipcode
            db.session.commit()
            db.session.flush
            uid = loggedinUser.id ## Get User id
            # Update Username in session
            session['username'] = fname
        except Exception as e:
            flash("Refresh Page! And Try Again")
            return redirect(url_for('users.checkout'))

        ## Place Order
        try:
            for item in session['shoppingCart']:
                order = Orders(user_id=uid, product_id=item, quantity=int(session['shoppingCart'][item]['quantity']))
                db.session.add(order)
                db.session.commit()
                # SEO Meta data
                meta = returnMeta('orderConfirm')
            return render_template('main/confirmation.html', meta=meta, categories=getCategories())
        except Exception as e:
            flash(f"Error Placing Your Order {str(e)}", "bg-red-200")
            return redirect(url_for('users.checkout'))

    # SEO Meta data
    meta = returnMeta('checkout')
    meta['title'] = "Checkout - " + session['username'] + " || " + params['blog_name']    
    return render_template('main/checkout.html', meta=meta, categories=getCategories(), form=form, user=loggedinUser)


# ----------- User Login ----------- #
@users.route("/login", methods=['GET', 'POST'])
def login():
    # Redirect User if logged in
    if 'user_logged_in' in session and 'username' in session:
        return redirect(url_for('users.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check If User Exists
        try:
            userExist = Users.query.filter_by(email=email).first()
            if not userExist:
                flash("User Doesn't Exists! Please Signup", "text-red-500")
                return redirect(url_for('users.login'))

            # Check email and password if user exists
            if check_password_hash(userExist.password, password):
                session['id'] = userExist.id
                session['username'] = userExist.name
                session['user_logged_in'] = True
                flash("Successfully! Signed in", "text-green-500")
                return redirect(url_for('users.dashboard'))
            else:
                flash("Incorrect Password! Try Again", "text-red-500")
                return redirect(url_for('users.login'))
        except Exception as e:
            flash(f"Incorrect Information! Try Again {str(e)}", "text-red-500")
            return redirect(url_for('users.login'))

    # SEO Meta data
    meta = returnMeta('login')
    return render_template('users/login.html', meta=meta, categories=getCategories(), form=form)

# ----------- User Signup ----------- #
@users.route("/signup", methods=['GET', 'POST'])
def signup():
    # Redirect User if logged in
    if 'user_logged_in' in session and 'username' in session:
        return redirect(url_for('users.dashboard'))

    form = UserRegisterForm()
    if form.validate_on_submit():
        fname = form.name.data
        fnumber = form.number.data
        femail = form.email.data
        fpassword = form.password.data
        fcpassword = form.cpassword.data
        faddress = form.address.data

        # Check if passwords are correct
        if fpassword != fcpassword:
            flash("Passwords Doesn't Matched! Try Again", "text-red-500")
            return redirect(url_for('users.signup'))

        password = generate_password_hash(fpassword, method="sha256")

        # Check If User Exists
        try:
            userExist = Users.query.filter_by(email=femail).first()
            if userExist:
                flash("Account Already Exists! Please Login", "text-red-500")
                return redirect(url_for('users.login'))

            # Signup if user doesn't exists
            userExist = Users(name=fname, number=fnumber, email=femail, password=password ,address=faddress)
            db.session.add(userExist)
            db.session.commit()
            flash("Successfully Signed Up! Please Login", "text-green-500")
            return redirect(url_for('users.login'))
        except Exception as e:
            flash("Incorrect Information! Try Again", "text-red-500")
            return redirect(url_for('users.signup'))

    # SEO Meta data
    meta = returnMeta('signup')
    return render_template('users/signup.html', meta=meta, categories=getCategories(), form=form)


## Cancel Order
@users.route("/cancelOrder", methods=['GET', 'POST'])
def cancelOrder():
    if request.method == "POST" and request.form.get('orderid'):
        id = request.form.get('orderid')
        try:
            order = Orders.query.filter_by(id=id).first()
            db.session.delete(order)
            db.session.commit()
            flash("Successfully! Cancelled your order", "text-red-500")
            return redirect(url_for('users.dashboard'))
        except Exception as e:
            flash("Refresh Page! And Try Again", "text-red-500")
            return redirect(url_for('users.dashboard'))

    return render_template('404.html')

# ----------- User Logout ----------- #
@users.route("/logout")
def logout():
    # Redirect User not if logged in
    if not 'user_logged_in' in session and not 'username' in session:
        flash("Please login to continue", "text-red-500")
        return redirect(url_for('users.login'))

    session.pop('id', None)
    session.pop('username', None)
    session.pop('user_logged_in', None)

    flash("Successfully Logged out", "text-red-500")
    return redirect(url_for('users.login'))