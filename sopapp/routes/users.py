from flask import Blueprint, render_template, request, flash, url_for, session, redirect

from ..models.users import Orders
from ..extensions import params, MergeDicts, getCategories, db

users = Blueprint('users', __name__, template_folder='templates')

# ----------- User Dashboard ----------- #
@users.route('/users')
def user():
    return "Welcome to your dashbaord"

# ----------- Shopping Cart ----------- #
### Add Product to cart and Display Cart
@users.route("/cart", methods=['GET', 'POST'])
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
        return render_template('users/empty-cart.html', params=params, categories=getCategories())

    return render_template('users/cart.html', params=params, categories=getCategories())

### Remove Cart Item
@users.route("/del", methods=['GET', 'POST'])
def delCartItem():
    pid = request.form.get('product_id')
    category = request.form.get('category')
    if pid and category and session['shoppingCart'][pid]['category'] == category:
        session['shoppingCart'].pop(pid, None)
        session.modified = True
    else:
        return render_template('error.html', msg="Internal Server Error")

    return redirect(request.referrer)
    

# ----------- Checkout ----------- #
@users.route("/checkout", methods=['GET', 'POST'])
def checkout():
    # Check if product are added in cart
    if session['shoppingCart'] == {}:
        msg = "Please select product to proceed to checkout"
        return render_template('cart.html', params=params, msg=msg)
    
    return render_template('users/checkout.html', params=params)

# ----------- Orders ----------- #
@users.route("/orders", methods=['GET', 'POST'])
### Receive Orders
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
                category_id = 1,
                product_id = i
            )
            db.session.add(customer)
            db.session.commit()
        return render_template('users/confirmation.html', params=params, msg=True, categories=getCategories())
    else:
        msg = "Please Enter Delivery Details"
        return render_template('users/checkout.html', params=params, msg=msg, categories=getCategories())

### Track Orders
@users.route("/trackorder")
def trackorder():
    trackid = request.form.get('trackid')
    return render_template('users/order.html', params=params)