# ----------- Flask Modules ----------- #
from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user

# ----------- Application Modules ----------- #
from ..models.main import Contacts, Products, Categories
from ..models.users import Users, Orders
from ..models.auth import LoginForm, AdminAdd, Admin, AdminRole
from ..extensions import db, roles
from ..functions import getCategories, authAdminRole

# ----------- Instiantiate Blueprint ----------- #
auth = Blueprint('auth', __name__, template_folder='templates', url_prefix='/admin')

# ----------- Dashboard ----------- #
@auth.route('/')
@login_required
def dashboard():
    data = {
        "totalCategories": Categories.query.count(),
        "totalProducts": Products.query.count(),
        "totalUsers": Users.query.count(),
        "contactedUsers": Contacts.query.count(),
        "totalOrders": Orders.query.count()
    }
    return render_template('admin/index.html', data=data, categories=getCategories())

# ----------- Login ----------- #
@auth.route('/login', methods=['GET', 'POST'])
#### Login User
def adminLogin():
    # Redirect User if logged in
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    form = LoginForm()
    ### Validate submission
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = True if request.form.get('remember') else False

        ## Check if User exists
        user = Admin.query.filter_by(email=email).first()
        if not user:
            flash("User Doesn't Exists", "text-danger")
            return redirect(url_for('auth.adminLogin'))
        elif check_password_hash(user.password, password):
            # Login User if correct password
            login_user(user, remember=remember)
            return redirect(url_for('auth.dashboard'))
        else:
            # Incorrect password
            flash("Try Again! Incorrect Password", "text-danger")
            return redirect(url_for('auth.adminLogin'))

    return render_template('admin/login.html', form=form)

# ----------- Logout ----------- #
@auth.route('/logout')
@login_required
def adminLogout():
    logout_user()
    return redirect(url_for('auth.adminLogin'))

# ----------- Account ----------- #
#### My Account View
@auth.route('/account', methods=['GET', 'POST'])
@login_required
def adminAccount():
    adminForm = AdminAdd() # Admin Add Form
    adminRoles = roles # Admin Roles
    admins = Admin.query.all() # Admin Database

    return render_template('admin/account.html', categories=getCategories(), adminForm=adminForm, adminRoles=adminRoles, admins=admins)

#### Add Admin
@auth.route('/account/add', methods=['GET', 'POST'])
@login_required
def adminAdd():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('auth.adminAccount'))

    adminForm = AdminAdd()
    ### Add Admin
    if adminForm.validate_on_submit:
        name = adminForm.name.data
        email = adminForm.email.data
        password = adminForm.password.data
        roles = adminForm.roles.data

        # Check if Admin Exists
        exist = Admin.query.filter_by(email=email).count()
        if exist > 0:
            flash("User Already Exists", "alert-danger")
            return redirect(url_for('auth.adminAccount'))

        ## Add Admin
        try:
            # Generate Password Hash
            password = generate_password_hash(password, method="sha256")
            # Add Admin
            query = Admin(name=name, email=email, password=password)
            db.session.add(query)
            db.session.commit()
            db.session.flush
            aid = query.id

            # Assign Roles to Admin
            for role in roles:
                entry = AdminRole(admin_id=aid, role_id=role)
                db.session.add(entry)
                db.session.commit()
            flash("Successfully! Added Admin", "alert-success")
            return redirect(url_for('auth.adminAccount'))
        except Exception as e:
            flash(f"Failed to add admin {e}", "alert-danger")
            return redirect(url_for('auth.adminAccount'))
    else:
        flash("Please Fill Complete Details", "alert-danger")
        return redirect(url_for('auth.adminAccount'))

#### Edit Admin
@auth.route('/account/edit', methods=['GET', 'POST'])
@login_required
def adminEdit():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('auth.adminAccount'))

    name = request.form.get('name')
    email = request.form.get('email')
    roles = request.form.getlist('roles')
    aid = request.form.get('aid')
    if name and email and roles and aid:
        ### Get Admin by Id
        try:
            query = Admin.query.filter_by(id=aid).first()
            ## Update Admin
            query.name = name
            query.email = email
            db.session.commit()
            ## Delete Admin Role Association
            adminRoles = AdminRole.query.filter_by(admin_id=aid).all()
            for role in adminRoles:
                db.session.delete(role)
                db.session.commit()
            ## Add New Admin Role Association
            for role in roles:
                newRole = AdminRole(admin_id = aid, role_id = role)
                db.session.add(newRole)
                db.session.commit()
            flash("Successfully! Edited Admin", "alert-success")
            return redirect(url_for('auth.adminAccount'))
        except Exception as e:
            flash("Error Updating Admin", "alert-danger")
            return redirect(url_for('auth.adminAccount'))
    else:
        flash("Please Fill Complete Details", "alert-danger")
        return redirect(url_for('auth.adminAccount'))

#### Delete Admin
@auth.route('/account/delete', methods=['GET', 'POST'])
@login_required
def adminDelete():
    ### Check if user has permission
    if not authAdminRole(current_user.id, 'admin'):
        flash('This page is not accessible', "alert-danger")
        return redirect(url_for('auth.adminAccount'))
        
    ### Delete Admins
    if request.method == "POST" and request.form.get('action') == "delete" and request.form.get('aid'):
        aid = request.form.get('aid')
        try:
            ## Delete Admin
            query = Admin.query.filter_by(id=aid).first()
            db.session.delete(query)
            db.session.commit()
            ## Delete Roles Association
            query = AdminRole.query.filter_by(admin_id=aid).all()
            for a in query:
                db.session.delete(a)
                db.session.commit()

            flash("Deleted Admin!", "alert-danger")
            return redirect(url_for('auth.adminAccount'))
        except Exception as e:
            flash("Error Deleting Roles", "alert-danger")
            return redirect(url_for('auth.adminAccount'))

    flash("Page Not Found")
    return redirect(url_for('main.error'))