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
    clicked_product = Product.get_product_by_name(product_name)[0]
    product_id = clicked_product.id
    purchased_this_product = False

    if current_user.is_authenticated:
        #uid = current_user.id -- we'll add this after getting more data
        uid = 1
        ret = Purchase.get_product_by_uid_pid(uid, product_id)
        purchased_this_product = ret[0] # boolean
        if purchased_this_product:
            # return render_template('test.html')
            purchased_product = ret[1]
            return render_template('products.html', pname=product_name,
            product=purchased_product, purchased_this_product=purchased_this_product)
    
    return render_template('products.html', pname=product_name,
            product=clicked_product, purchased_this_product=purchased_this_product)
    

    

