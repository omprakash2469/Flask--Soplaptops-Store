# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, request, flash, url_for, session, redirect

# ----------- Application Modules ----------- #
from ..models.main import Products, ProductsImages
from ..models.users import Orders, OrdersForm
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
            url = url_for('static', filename=f"assets/images/{category}/{image.image_name}") # Get product image

            ## Add Product to Cart
            cartItems = {
                pid : {
                    'category': category,
                    'name': product.product,
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


    return render_template('users/empty-cart.html', params=params, categories=getCategories())

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
        name = form.name.data
        number = form.number.data
        email = form.email.data
        street = form.street.data
        address = form.address.data
        zipcode = form.zipcode.data
        place_order = form.place_order.data

        ## Register User - unique email
        ## Place Order
    return render_template('users/checkout.html', params=params, categories=getCategories(), form=form)

# ----------- Orders ----------- #
@users.route("/orders", methods=['GET', 'POST'])
### Receive Orders
def orders():
    if session['shoppingCart'] == {}:
        flash("Please make a purchase", "bg-green-200")
        return redirect(url_for('users.userCart'))

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
                category_id = 1,
                product_id = i
            )
            db.session.add(customer)
            db.session.commit()
        return render_template('users/confirmation.html', params=params, msg=True, categories=getCategories())
    else:
        msg = "Please Enter Delivery Details"
        return render_template('users/checkout.html', params=params, msg=msg, categories=getCategories())

# ----------- User Dashboard ----------- #
@users.route("/dashboard")
def dashboard():
    trackid = request.form.get('trackid')
    return render_template('users/order.html', params=params)