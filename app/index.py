import math  # "Any modules that are part of Python's standard library such as math , os , sys , etc do not need to be listed in your requirements. txt file"

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired, NumberRange

from .models.product import Product
from .models.purchase import Purchase
from .models.rated import Rated
from .models.user import User
from .models.seller import Seller
from .ratings import AddRatingForm

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    # render the page by adding information to the index.html file

    return render_template('index.html',
                           avail_products=products)


@bp.route('/profile/<uid>', methods=['GET', 'POST'])
def get_profile(uid):
    user_profile = User.get(uid)
    avg_rating = Seller.avg_rating_for_seller(uid)
    # print("avg rating: ", avg_rating)
    integer_rating = get_integer_rating(avg_rating)
    ceiling = get_ceiling(avg_rating)
    num_ratings = Seller.num_ratings_for_seller(uid)
    num_ratings = format_num_ratings(num_ratings)

    if request.method == 'POST':
        if current_user.is_authenticated:
            buyer_id = current_user.id
            already_rated = Seller.already_rated(uid, buyer_id)
            if already_rated:
                flash('Already rated this seller!')
                return redirect(url_for('index.get_profile', uid=uid))
            else:
                rating = request.form.get('Rating')
                result = Seller.add_rating(uid, buyer_id, rating)
                flash('Rating added successfully!')
                return redirect(url_for('index.get_profile', uid=uid))

    return render_template('profile.html',
                           user_profile=user_profile,
                           avg_rating=avg_rating, ceiling=ceiling,
                           integer_rating=integer_rating,
                           num_ratings=num_ratings)


@bp.route('/add_rating_seller/<seller_id>', methods=['GET', 'POST'])
def add_rating_seller(seller_id):
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id
    uid = current_user.id
    if request.method == 'POST':
        if current_user.is_authenticated:
            already_rated = Rated.already_rated(uid, pid)
            if already_rated:
                flash('Already rated this product!')
                return redirect(url_for('index.display_product', product_name=product_name))
            else:
                rating = request.form.get('Rating')
                result = Rated.add_rating(uid, pid, rating)
                flash('Rating added successfully!')
                return redirect(url_for('index.display_product', product_name=product_name))
    else:
        flash('Invalid rating')
        return redirect(url_for('index.display_product', user_profile=user_profile))


class AddToCartForm(FlaskForm):
    pid = HiddenField()
    seller = SelectField('Seller', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
                            InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Cart')


def get_integer_rating(avg_rating):
    integer_rating = 0
    for a in avg_rating:
        if avg_rating != [(None,)]:
            integer_rating = int(a['rating'])
    return integer_rating


def get_ceiling(avg_rating):
    ceiling = 0
    for a in avg_rating:
        if avg_rating != [(None,)]:
            ceiling = math.ceil(a['rating'] - int(a['rating']))
    print(ceiling)
    print("type: ", type(ceiling))
    return int(ceiling)


def format_num_ratings(num_ratings):
    print("Number of ratings for product/seller: ", num_ratings)
    for num in num_ratings:
        num_ratings = int(num['num_ratings'])
    return num_ratings


@bp.route('/products/<product_name>/')
def display_product(product_name):
    """ Displays the product. 'product_name' is also the name of img file
    """
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id

    purchased_this_product = False
    sellers_and_quantities = Product.get_sellers_and_quantities_for_product(
        product_name)
    add_to_cart_form = AddToCartForm(pid=pid)
    # print("sellers and quanitites: ", sellers_and_quantities)

    avg_rating = Rated.avg_rating_for_product(pid)
    integer_rating = int(avg_rating)
    # integer_rating = get_integer_rating(avg_rating)

    num_ratings = Rated.num_ratings_for_product(pid)
    # num_ratings = format_num_ratings(num_ratings)

    if current_user.is_authenticated:
        uid = current_user.id
        ret = Purchase.get_product_by_uid_pid(uid, pid)
        purchased_this_product = ret[0]  # boolean
        # print(sellers_and_quantities)
        add_to_cart_form.seller.choices = [
            (val['seller_id'], val['firstname'] + " " + val['lastname']) for val in sellers_and_quantities]
        if purchased_this_product:
            purchased_product = ret[1]
            already_rated = Rated.already_rated(uid, pid)
            return render_template('view_product.html', pname=product_name,
                                   product=product, purchase=purchased_product, purchased_this_product=purchased_this_product,
                                   sellers_and_quantities=sellers_and_quantities,
                                   add_to_cart_form=add_to_cart_form, avg_rating=avg_rating,
                                   integer_rating=integer_rating, num_ratings=num_ratings)
    return render_template('view_product.html', pname=product_name,
                           product=product, purchased_this_product=purchased_this_product,
                           add_rating_form=AddRatingForm(), sellers_and_quantities=sellers_and_quantities,
                           add_to_cart_form=add_to_cart_form, avg_rating=avg_rating,
                           integer_rating=integer_rating, num_ratings=num_ratings)


@bp.route('/add_rating/<product_name>', methods=['GET', 'POST'])
def add_rating(product_name):
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id
    uid = current_user.id
    if request.method == 'POST':
        if current_user.is_authenticated:
            already_rated = Rated.already_rated(uid, pid)
            # Rated.add_rating(current_user.id, product_id, rating)
            if already_rated:
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

def get_reviews_and_names(product_name):
    product = Product.get_product_by_name(product_name)[0]
    pid = product.id
    reviews = Rated.get_all_reviews_by_pid(pid)
    review_dict = {}

    for review in reviews:
        uid = review['uid']
        review_and_name = Rated.get_reviews_and_reviewers_by_pid_uid(pid, uid)[0]

        name = review_and_name['firstname'] + " " + review_and_name['lastname']
        review = review_and_name['review']
        upvotes = review_and_name['upvotes']
        time_added = review_and_name['time_added']
        review_dict[uid] = [upvotes, time_added, name, review, uid]

        review_dict[uid]= [upvotes, time_added, name, review, uid]
    
    sorted_by_upvotes = sorted(list(review_dict.values()), key=lambda x: x[0], reverse=True)
    top3 = sorted_by_upvotes[0:3]
    remaining = sorted_by_upvotes[3:]

    remaining_sorted_by_time = sorted(remaining, key=lambda x: x[1], reverse=True)
    final_list = top3 + remaining_sorted_by_time

    return final_list  # top3 by number of upvotes, then by time

@bp.route('/<product_name>/product-reviews', methods=['GET', 'POST'])
def display_reviews(product_name):
    pid =  Product.get_pid(product_name)
    reviewer_uid = current_user.id
    if request.method == 'POST':
        print("request method is post")
        if current_user.is_authenticated:
            uid = current_user.id
            upvote_receiver_uid = request.form.get('receiver_uid')
            if request.form.get('upvote') != None:  # an upvote request
                upvote_receiver_uid = int(upvote_receiver_uid)
                if Rated.already_upvoted(upvote_receiver_uid, pid, current_user.id):# check if already upvoted
                    flash('Already upvoted this review!')
                    # msg = 'Already upvoted this review!'
                    reviews_and_names = get_reviews_and_names(product_name)
                    return render_template("reviews2.html", pname=product_name,
                                           reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                           reviewer_uid=reviewer_uid)
                # else add the upvote to upvote_receiver_uid
                current_upvotes = Rated.get_current_upvotes(upvote_receiver_uid, pid)['current_upvotes']
                # last upvoted by current user id (uid)
                result = Rated.add_upvote(upvote_receiver_uid, pid, current_upvotes)
                result2 = Rated.record_upvote(upvote_receiver_uid, pid, current_user.id)
                flash('Review upvoted!')
                # msg2 = 'Review upvoted!'
                reviews_and_names = get_reviews_and_names(product_name)
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid)

            already_reviewed = Rated.already_reviewed(uid, pid)
            reviewer_uid = current_user.id
            if already_reviewed:
                flash('Already reviewed this product!')
                # msg3 = 'Already reviewed this product!'
                reviews_and_names = get_reviews_and_names(product_name)
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid)
            else:
                review = request.form.get('review')
                result = Rated.add_review(uid, pid, review)
                flash('Review added successfully!')
                # msg4 = 'Review added successfully!'
                reviews_and_names = get_reviews_and_names(product_name)
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid)
    else:
        reviews_and_names = get_reviews_and_names(product_name)
        return render_template("reviews2.html", pname=product_name,
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=None, reviewer_uid=None)



@bp.route('/<uid>/seller-reviews', methods=['GET', 'POST'])
def seller_reviews(uid):
    reviews = Seller.get_all_reviews_by_sid(uid)
    usernames = []
    reviews_and_names = []
    for review in reviews:
        print("review: ", review)
        bid = review['bid']
        review_and_name = Seller.get_reviewers_by_bid(bid)[0]
        reviews_and_names.append(review_and_name)

    if request.method == 'POST':
        if current_user.is_authenticated:
            already_rated = Rated.already_rated(uid, pid)
            # Rated.add_rating(current_user.id, product_id, rating)
            if already_rated:
                flash('Already rated this product!')
                return redirect(url_for('index.display_product', product_name=product_name))
            else:
                rating = request.form.get('Rating')
                result = Rated.add_rating(uid, pid, rating)
                flash('Rating added successfully!')
                return redirect(url_for('index.seller_reviews', uid=uid,
                                        reviews_and_names=reviews_and_names))

    return render_template("seller_reviews.html", uid=uid,
                           reviews_and_names=reviews_and_names)
