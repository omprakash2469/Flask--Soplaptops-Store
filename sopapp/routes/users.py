# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, request, flash, url_for, session, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# ----------- Application Modules ----------- #
from ..models.users import Orders, OrdersForm, Users, UserRegisterForm
from ..models.main import Products, ProductsImages
from ..models.auth import LoginForm
from ..extensions import params, db
from ..functions import MergeDicts, getCategories, getCategoryById

# ----------- Instiantiate Blueprint ----------- #
users = Blueprint('users', __name__, template_folder='templates')

# ----------- User Dashboard ----------- #
@users.route('/users')
def user():
    return "Welcome to your dashbaord"

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
                    'price': product.price,
                    'quantity': quantity,
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


    return render_template('main/empty-cart.html', params=params, categories=getCategories())

### Return Cart Item
@users.route("/returnitems", methods=['GET', 'POST'])
def returnItems():
    items = jsonify(session['shoppingCart'])
    return items

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
    if session['shoppingCart'] == {}:
        flash("Please make a purchase", "bg-green-200")
        return redirect(url_for('users.userCart'))

    form = OrdersForm()
    if form.validate_on_submit():
        fname = form.name.data
        fnumber = form.number.data
        femail = form.email.data
        fstreet = form.street.data
        faddress = form.address.data
        fzipcode = form.zipcode.data

        ## User Authentication
        # Check if User Exists
        userExist = Users.query.filter_by(email=femail).first()
        if not userExist:
            # Create User Password
            password = generate_password_hash(secrets.token_urlsafe(14), method="sha256")
            # Register User if user not exists
            try:
                register = Users(
                    name = fname,
                    number = fnumber,
                    email = femail,
                    password = password,
                    street = fstreet,
                    address = faddress,
                    zipcode = fzipcode
                )
                db.session.add(register)
                db.session.commit()
                db.session.flush
                uid = register.id
            except Exception as e:
                flash("Refresh Page! And Try Again")
                return redirect(url_for('users.checkout'))
        else:
            uid = userExist.id

        ## Place Order
        try:
            for item in session['shoppingCart']:
                order = Orders(user_id=uid, product_id=item)
                db.session.add(order)
                db.session.commit()

            return render_template('main/confirmation.html', params=params, categories=getCategories())
        except Exception as e:
            flash("Error Placing Your Order", "bg-red-200")
            return redirect(url_for('users.checkout'))

    return render_template('main/checkout.html', params=params, categories=getCategories(), form=form)


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
        remember = True if request.form.get('remember') else False

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
            
    return render_template('users/login.html', params=params, categories=getCategories(), form=form)

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

    return render_template('users/signup.html', params=params, categories=getCategories(), form=form)

# ----------- User Dashboard ----------- #
@users.route("/dashboard")
def dashboard():
    # Redirect User if not logged in
    if not 'user_logged_in' in session and not 'username' in session:
        flash("Please login to continue", "text-red-300")
        return redirect(url_for('users.login'))
    
    ### Get current loggedin's user orders
    userOrders = Orders.query.filter_by(user_id=session['id']).all()
    for order in userOrders:
        ## Get Product Information by product id
        product = Products.query.filter_by(id=order.product_id).first()
        category = getCategoryById(product.category_id) # Get category of product
        image = ProductsImages.query.filter_by(product_id=product.id).first()
        url = url_for('static', filename=f"assets/images/products/{category}/{image.image_name}") # Get product image

        ## Add Product to Cart
        orders = {
            product.id : {
                'category': category,
                'name': product.product,
                'product_url': url_for('main.singleProductPage', category=category, slug=product.product.replace(' ', '-').lower()),
                'price': product.price,
                'quantity': product.quantity,
                'image': url
            }
        }
    
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

    return render_template('users/index.html', params=params, categories=getCategories(), orders=orders, user=user)

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