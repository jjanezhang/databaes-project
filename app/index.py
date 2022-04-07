from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired

import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.user import User
from .models.rated import Rated
from .ratings import AddRatingForm

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

@bp.route('/profile/<uid>', methods=['GET'])
def get_profile(uid):
    user_profile = User.get(uid)
    return render_template('profile.html',
                        user_profile=user_profile)

class AddToCartForm(FlaskForm):
    seller = SelectField('Seller', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Cart')
                           
@bp.route('/products/<product_name>/')
def display_product(product_name):
    """ Displays the product. 'product_name' is also the name of img file
    """
    clicked_product = Product.get_product_by_name(product_name)[0]
    product_id = clicked_product.id
    purchased_this_product = False
    sellers_and_quantities = Product.get_sellers_and_quantities_for_product(product_name)
    add_to_cart_form = AddToCartForm()

    if current_user.is_authenticated:
        uid = current_user.id 
        ret = Purchase.get_product_by_uid_pid(uid, product_id)
        purchased_this_product = ret[0] # boolean
        print(sellers_and_quantities)
        add_to_cart_form.seller.choices = [(val['pid'], val['firstname'] + " " + val['lastname']) for val in sellers_and_quantities]
        if purchased_this_product:
            purchased_product = ret[1]
            return render_template('view_product.html', pname=product_name,
            product=clicked_product, purchase=purchased_product, purchased_this_product=purchased_this_product,
            sellers_and_quantities=sellers_and_quantities, add_to_cart_form=add_to_cart_form)
    
    return render_template('view_product.html', pname=product_name,
            product=clicked_product, purchased_this_product=purchased_this_product,
            add_rating_form = AddRatingForm(), sellers_and_quantities=sellers_and_quantities,
            add_to_cart_form=add_to_cart_form)
    
@bp.route('/products/')
def all_products():
    avail_products = Product.get_all(True)
    return render_template('products.html', avail_products=avail_products)

@bp.route('/add_rating/<product_name>', methods=['GET','POST'])
def add_rating(product_name):
    # return "Failure!"
    product = Product.get_product_by_name(product_name)[0]
    product_id = product.id
    # product_id =1
    if request.method == 'POST':
        # return "POST!" # works
        if current_user.is_authenticated:
            # return "AUTHENTICATED!" # works
            rating = request.form.get('Rating')
            if Rated.add_rating(current_user.id, product_id, rating):
                # return 'Rating added!'
                return redirect(url_for('index.display_product', product_name=product_name))
        #review = request.form.get('Review')
    #return redirect(url_for('index.display_product', product_name=product_name))
    return "NOT!"
    # return redirect(url_for('ratings.index'))

