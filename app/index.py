import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired, NumberRange

from .models.product import Product
from .models.purchase import Purchase
from .models.rated import Rated
from .models.user import User
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
    pid = HiddenField()
    seller = SelectField('Seller', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Cart')
                           
@bp.route('/products/<product_name>/')
def display_product(product_name):
    """ Displays the product. 'product_name' is also the name of img file
    """
    product = Product.get_product_by_name(product_name)[0]
    if product ==None:
        return render_template("fail.html")
    pid = product.id

    purchased_this_product = False
    sellers_and_quantities = Product.get_sellers_and_quantities_for_product(product_name)
    add_to_cart_form = AddToCartForm(pid = pid)

    avg_rating = Rated.avg_rating_for_product(pid)
    integer_rating =0
    for a in avg_rating:
        if avg_rating != [(None,)]:
            print("a in avg rating: " , a)
            integer_rating = int(a['rating'])
    # print(type(avg_rating))

    num_ratings = Rated.num_ratings_for_product(pid)
    for num in num_ratings:
        num_ratings = int(num['num_ratings'])

    if current_user.is_authenticated:
        uid = current_user.id 
        ret = Purchase.get_product_by_uid_pid(uid, pid)
        purchased_this_product = ret[0] # boolean
        # print(sellers_and_quantities)
        add_to_cart_form.seller.choices = [(val['sid'], val['firstname'] + " " + val['lastname']) for val in sellers_and_quantities]
        if purchased_this_product:
            purchased_product = ret[1]
            already_rated = Rated.already_rated(uid, pid)
            return render_template('view_product.html', pname=product_name,
            product=product, purchased_this_product=purchased_this_product,
            sellers_and_quantities=sellers_and_quantities, 
            add_to_cart_form=add_to_cart_form, avg_rating=avg_rating, 
            integer_rating =integer_rating, num_ratings=num_ratings)
    
    return render_template('view_product.html', pname=product_name,
            product=product, purchased_this_product=purchased_this_product,
            add_rating_form = AddRatingForm(), sellers_and_quantities=sellers_and_quantities,
            add_to_cart_form=add_to_cart_form, avg_rating=avg_rating, 
            integer_rating =integer_rating, num_ratings=num_ratings)

@bp.route('/add_rating/<product_name>', methods=['GET','POST'])
def add_rating(product_name):
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id
    uid = current_user.id
    if request.method == 'POST':
        if current_user.is_authenticated:
            already_rated = Rated.already_rated(uid, pid)
            if already_rated: #Rated.add_rating(current_user.id, product_id, rating)
                flash('Already rated this product!')
                return redirect(url_for('index.display_product', product_name=product_name))
            else:
                rating = request.form.get('Rating')
                result = Rated.add_rating(uid, pid, rating)
                flash('Rating added successfully!')
                return redirect(url_for('index.display_product', product_name=product_name))
    else:
        flash('Invalid rating')
        return redirect(url_for('index.display_product', product_name=product_name))
    # return redirect(url_for('ratings.index'))

@bp.route('/<product_name>/reviews')
def display_reviews(product_name):
    # return render_template("fail.html")
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id
    reviews = Rated.get_all_reviews_by_pid(pid)
    usernames = []
    reviews_and_names = []
    for review in reviews:
        print("review: ", review)
        uid = review['uid']
        review_and_name = Rated.get_reviews_and_reviewers_by_pid_uid(pid, uid)[0]
        # print("review+ reviewer: ", review_and_name)
        reviews_and_names.append(review_and_name)
        # user = User.get_names(uid)[0]
        # username = user['firstname']+ " " + user['lastname']
        # usernames.append(username)
        # print("user: ", both['firstname']+ " " + both['lastname'])
        # for u in user:
        #     print("u: ", u)
    return render_template("reviews.html", pname=product_name, reviews=reviews,
    usernames=usernames, reviews_and_names=reviews_and_names)