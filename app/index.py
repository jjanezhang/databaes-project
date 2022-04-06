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

class AddRatingForm(FlaskForm):
    #pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Add Rating')

class RatingsForm(FlaskForm):
    #pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Update Rating')

@bp.route('/products/<product_name>/add_rating', methods=['GET','POST'])
def add_rating(product_name):
    add_rating_form = AddRatingForm()
    pid = Product.get_product_by_name(product_name)[0].id

    if current_user.is_authenticated and add_rating_form.validate_on_submit():
        if Rated.add_rating(current_user.id, pid, add_rating_form.new_rating.data):
            return redirect(url_for('index.index'))
    return render_template('products.html',
                            ratings_form=ratings_form,
                            add_rating_form=add_rating_form,
                            product_name=product_name, pid=pid)

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

                           
@bp.route('/products/<product_name>/')
def display_product(product_name):
    """ Displays the product. 'product_name' is also the name of img file
    """
    clicked_product = Product.get_product_by_name(product_name)[0]
    product_id = clicked_product.id
    purchased_this_product = False

    if current_user.is_authenticated:
        uid = current_user.id #-- we'll add this after getting more data
        ret = Purchase.get_product_by_uid_pid(uid, product_id)
        purchased_this_product = ret[0] # boolean
        if purchased_this_product:
            # return render_template('test.html')
            purchased_product = ret[1]
            return render_template('view_product.html', pname=product_name,
            product=purchased_product, purchased_this_product=purchased_this_product)
    
    return render_template('view_product.html', pname=product_name,
            product=clicked_product, purchased_this_product=purchased_this_product,
            add_rating_form = AddRatingForm())
    
@bp.route('/products/')
def all_products():
    avail_products = Product.get_all(True)
    return render_template('products.html', avail_products=avail_products)
