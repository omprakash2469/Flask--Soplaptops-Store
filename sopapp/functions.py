from flask import redirect, url_for
import re
from .models.main import Products, Categories, ProductsImages
from .models.auth import AdminRole, Admin
from .extensions import roles
from sopapp import login_manager

# ----------- Login Manager ----------- #
login_manager.login_view = 'auth.adminLogin'
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def adminById(id):
    admin = Admin.query.get(id)
    return admin.name

# ----------- Function for Jinja ----------- #
## Get Number of products by category id
def NumberOfProducts(id):
    try:
        query = Products.query.filter_by(category_id=id).count()
        return query
    except:
        return redirect(url_for('main.error'))

# ----------- Slug Format ----------- #
def slugFormat(string):
    string = re.sub('[^a-zA-Z0-9 \n\.]', '', string)
    return " ".join(string.strip().lower().split()).replace(' ', '-')

def getProductImages(bool, *id):
    if id and bool:
        images = ProductsImages.query.filter_by(product_id=id[0]).all()
        return images
    elif(id and not bool):
        image = ProductsImages.query.filter_by(product_id=id[0]).first()
        return image.image_name
    else:
        return False


## Get Category Name by id
def getCategoryById(id):
    try:
        categories = Categories.query.filter_by(id=id).first()
        return categories.category.lower() # return category name
    except:
        return redirect(url_for('main.error'))

## Get Roles Id by admin Id
def roleIdByAdminId(id):
    try:
        adminRoles = AdminRole.query.filter_by(admin_id=id).all()
        r = []
        for role in adminRoles:
            r.append(role.role_id)
        return r
    except:
        return redirect(url_for('main.error'))

## Get Role by admin Id
def roleByAdminId(id):
    try:
        adminRoles = AdminRole.query.filter_by(admin_id=id).first()
        role = roles[adminRoles.role_id]['role']
        return role
    except:
        return redirect(url_for('main.error'))
        
    ## Authenticate User Roles
def authAdminRole(id, role):
    # Get role id by role name
    rid = 0
    for r in roles:
        if roles[r]['role'] == role:
            rid = r
            break
    # Check  if role is assigned to user
    authRole  = AdminRole.query.filter_by(admin_id=id, role_id=rid).count()
    if authRole == 1:
        return True
    else:
        return  False

# Get Categories
def getCategories():
    return Categories.query.all()

# Merge two Dictionary
def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

# Subtotal at checkout
def returnSum(dict):
    sum = 0
    for key in dict:
        sum = sum + int(dict[key]['price'])
    return sum

# Convert raw product details data into html format
def productDetailsFormat(string, method):
    if method:
        # Replace Heading
        string = string.replace("[", '<div class="mb-1"><h5 class="text-lg font-lato font-semibold">')
        string = string.replace("]", '</h5>')
        
        # Replace Paragraph
        string = string.replace("(", '<p class="font-source text-lg text-gray-600">')
        string = string.replace(")", '</p></div>')
        return string
    else:
        # Replace Heading
        string = string.replace('<div class="mb-1"><h5 class="text-lg font-lato font-semibold">', "[")
        string = string.replace('</h5>', "]")
        
        # Replace Paragraph
        string = string.replace('<p class="font-source text-lg text-gray-600">', "(")
        string = string.replace('</p></div>', ")")
        return string


func_dict = {
    "NumberOfProducts":  NumberOfProducts,
    "getCategoryById":  getCategoryById,
    "roleIdByAdminId":  roleIdByAdminId,
    "authAdminRole":  authAdminRole,
    "getCategories": getCategories,
    "MergeDicts": MergeDicts,
    "roleByAdminId": roleByAdminId,
    "returnSum": returnSum,
    "getProductImages": getProductImages
}