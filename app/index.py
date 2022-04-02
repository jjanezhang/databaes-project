from flask import Blueprint, render_template
from flask_login import current_user

import datetime

from .models.product import Product
from .models.purchase import Purchase

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)
                           
@bp.route('/products/<product_name>/')
def display_product(product_name):
    """ Displays the product. 'product_name' is also the name of img file
    """
    #p_name= product_name.name
    this_product = Product.get_product_by_name(product_name)
    product_id = this_product[0].id
    purchased = True

    if current_user.is_authenticated:
        #uid = current_user.id
        uid = 1
        purchased = Purchase.get_product_by_uid_pid(uid, product_id)
        if not purchased:
            purchased = False

    return render_template('products.html', pname=product_name,
        product=this_product, purchased=purchased)

