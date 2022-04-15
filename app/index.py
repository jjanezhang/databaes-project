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
    # get all available products and their info for sale:
    products = Product.get_all()
    ratingsData = Rated.ratings_for_all_products()

    # pids = [product.id for product in products]
    # avg_ratings = [Rated.avg_rating_for_product(pid) for pid in pids]
    # integer_ratings = [int(avg_rating) for avg_rating in avg_ratings]
    # num_ratings = [Rated.num_ratings_for_product(pid) for pid in pids]

    avg_ratings = list(map(lambda x: x['avg_rating'], ratingsData))
    integer_ratings = [int(avg_rating) for avg_rating in avg_ratings]
    num_ratings = list(map(lambda x: x['num_ratings'], ratingsData))

    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,integer_ratings=integer_ratings,
                           avg_ratings=avg_ratings, num_ratings=num_ratings)


@bp.route('/profile/<uid>', methods=['GET', 'POST'])
def get_profile(uid):
    user_profile = User.get(uid)
    seller_id = uid
    avg_rating = Seller.avg_rating_for_seller(uid)
    integer_rating = int(avg_rating)
    ceiling = math.ceil(avg_rating - int(avg_rating)) # get_ceiling(avg_rating)
    num_ratings = Seller.num_ratings_for_seller(uid)
    bought_from_this_seller = False
    if current_user.is_authenticated:
        buyer_id = current_user.id
        bought_from_this_seller = Seller.check_bought_by_sid_bid(seller_id, buyer_id)

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

    return render_template('profile2.html',
                           user_profile=user_profile,
                           avg_rating=avg_rating, ceiling=ceiling,
                           integer_rating=integer_rating,
                           num_ratings=num_ratings, bought_from_this_seller=bought_from_this_seller)

class AddToCartForm(FlaskForm):
    pid = HiddenField()
    seller = SelectField('Seller', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
                            InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Cart')

@bp.route('/products/<product_name>/')
def display_product(product_name):
    product = Product.get_product_by_name(product_name)[0]
    pid = product['id'] #product.id
    purchased_this_product = Purchase.check_purchased_by_uid_pid(current_user.id, pid)
    sellers_and_quantities = Product.get_sellers_and_quantities_for_product(
        product_name)
    add_to_cart_form = AddToCartForm(pid=pid)
    avg_rating = Rated.avg_rating_for_product(pid)
    integer_rating = int(avg_rating)
    num_ratings = Rated.num_ratings_for_product(pid)

    if current_user.is_authenticated:
        uid = current_user.id
        add_to_cart_form.seller.choices = [
            (val['seller_id'], val['firstname'] + " " + val['lastname']) for val in sellers_and_quantities]
        if purchased_this_product:
            purchased_product = None #ret[1]
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

@bp.route('/add_rating_seller/<seller_id>', methods=['GET', 'POST'])
def add_rating_seller(seller_id):
    buyer_id = current_user.id
    if request.method == 'POST':
        if current_user.is_authenticated:
            already_rated = Seller.already_rated(seller_id, buyer_id)
            if already_rated:
                flash('Already rated this seller!')
                return redirect(url_for('index.get_profile', uid=seller_id))
            else:
                rating = request.form.get('Rating')
                # current_review= ""
                # if Seller.already_reviewed(seller_id, buyer_id):
                #     current_review = Seller.get_current_review_and_upvote(seller_id, buyer_id)

                result = Seller.add_rating(seller_id, buyer_id, rating)
                flash('Rating added successfully!')
                return redirect(url_for('index.get_profile', uid=seller_id))
    else:
        # flash('Invalid rating')
        return redirect(url_for('index.get_profile', uid=seller_id))

def get_reviews_and_names(product_name, for_product=True, sid=None):
    if for_product:
        product = Product.get_product_by_name(product_name)[0]
        pid = product.id
        reviews = Rated.get_all_reviews_for_pid(pid) #Rated.get_all_reviews_by_pid(pid)
        review_dict = {}
        this_user_review = ""
        for review in reviews:
            uid = review['uid']
            if review['uid']==current_user.id:
                this_user_review = review['review']
            if review['review'] =="" or review['uid']==current_user.id: # don't double count
                continue
            # review_and_name = Rated.get_reviews_and_reviewers_by_pid_uid(pid, uid)[0]
            review_and_name = review
            upvotes = review_and_name['upvotes'] # rn[0]
            time_added = review_and_name['time_added'] # rn[1]
            name = review_and_name['firstname'] + " " + review_and_name['lastname'] # rn[2]
            review = review_and_name['review'] # rn[3]
            review_dict[uid] = [upvotes, time_added, name, review, uid] # uid = rn[4]
        
        sorted_by_upvotes = sorted(list(review_dict.values()), key=lambda x: x[0], reverse=True)
        top3 = sorted_by_upvotes[0:3]
        remaining = sorted_by_upvotes[3:]

        remaining_sorted_by_time = sorted(remaining, key=lambda x: x[1], reverse=True)
        final_list = top3 + remaining_sorted_by_time
        return [final_list,this_user_review]  # top3 by number of upvotes, then by time

    else: # if not for product but for seller
        reviews = Seller.get_all_reviews_for_sid(sid)
        # print("got reviews for sellers: ", reviews)
        review_dict = {}
        this_user_review = ""
        for review in reviews:
            uid = review['bid']
            # review_and_name = Rated.get_reviews_and_reviewers_by_pid_uid(pid, uid)[0]
            if review['bid']==current_user.id:
                this_user_review = review['review']
            if review['review'] =="" or review['bid']==current_user.id: # don't double count
                continue
            review_and_name = review
            upvotes = review_and_name['upvotes'] # rn[0]
            time_added = review_and_name['time_added'] # rn[1]
            name = review_and_name['firstname'] + " " + review_and_name['lastname'] # rn[2]
            review = review_and_name['review'] # rn[3]
            review_dict[uid] = [upvotes, time_added, name, review, uid] # uid = rn[4]
        
        sorted_by_upvotes = sorted(list(review_dict.values()), key=lambda x: x[0], reverse=True)
        top3 = sorted_by_upvotes[0:3]
        remaining = sorted_by_upvotes[3:]

        remaining_sorted_by_time = sorted(remaining, key=lambda x: x[1], reverse=True)
        final_list = top3 + remaining_sorted_by_time
        return [final_list, this_user_review]  # top3 by number of upvotes, then by time

@bp.route('/<product_name>/product-reviews', methods=['GET', 'POST'])
def display_reviews(product_name):
    pid =  Product.get_pid(product_name)
    reviewer_uid = None
    upvote_receiver_uid = None
    purchased_this_product = Purchase.check_purchased_by_uid_pid(current_user.id, pid)
    already_reviewed = Rated.already_reviewed(current_user.id, pid) #(uid, pid)

    got_any_reviews = True
    if request.method == 'POST':
        if current_user.is_authenticated:
            uid = current_user.id
            upvote_receiver_uid = request.form.get('receiver_uid')
            print("got upvote receiver uid = ", upvote_receiver_uid)
            if request.form.get('upvote') != None:  # an upvote request
                upvote_receiver_uid = int(upvote_receiver_uid)
                if Rated.already_upvoted(upvote_receiver_uid, pid, current_user.id):# check if already upvoted
                    flash('Already upvoted this review!')
                    review_list = get_reviews_and_names(product_name)
                    reviews_and_names = review_list[0]
                    if reviews_and_names==[]:
                        got_any_reviews=False
                    return render_template("reviews2.html", pname=product_name,
                        reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                        reviewer_uid=reviewer_uid, purchased_this_product=purchased_this_product,
                        already_reviewed=already_reviewed, got_any_reviews=got_any_reviews, this_user_review=review_list[1])
                # else add the upvote to upvote_receiver_uid
                current_upvotes = Rated.get_current_upvotes(upvote_receiver_uid, pid)['current_upvotes']
                result = Rated.add_upvote(upvote_receiver_uid, pid, current_upvotes)
                result2 = Rated.record_upvote(upvote_receiver_uid, pid, current_user.id)
                flash('Review upvoted!')
                review_list = get_reviews_and_names(product_name)
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid, purchased_this_product=purchased_this_product,
                                       already_reviewed=already_reviewed, got_any_reviews=got_any_reviews, this_user_review=review_list[1])

            # already_reviewed = Rated.already_reviewed(uid, pid)
            reviewer_uid = current_user.id  # a post request that is not 'upvote'== a review request by current user
            if already_reviewed:
                flash('Already reviewed this product!')
                review_list = get_reviews_and_names(product_name)
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid, purchased_this_product=purchased_this_product,
                                       already_reviewed=already_reviewed, got_any_reviews=got_any_reviews, this_user_review=review_list[1])
            else:
                review = request.form.get('review')
                result = Rated.add_review(uid, pid, review)
                flash('Review added successfully!')
                review_list = get_reviews_and_names(product_name)
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False
                return render_template("reviews2.html", pname=product_name,
                                       reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid,
                                       reviewer_uid=reviewer_uid, purchased_this_product=purchased_this_product,
                                       already_reviewed=already_reviewed, got_any_reviews=got_any_reviews, this_user_review=review_list[1])
    else:
        review_list = get_reviews_and_names(product_name)
        reviews_and_names = review_list[0]
        if reviews_and_names==[]:
            got_any_reviews=False
        return render_template("reviews2.html", pname=product_name,
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=None, 
                           reviewer_uid=None, purchased_this_product=purchased_this_product,
                           already_reviewed=already_reviewed, got_any_reviews=got_any_reviews, this_user_review=review_list[1])

@bp.route('/<uid>/seller-reviews', methods=['GET', 'POST'])
def seller_reviews(uid):
    reviewer_uid = None
    upvote_receiver_uid = None
    bought_from_this_seller = False
    if current_user.is_authenticated:
        bought_from_this_seller = Seller.check_bought_by_sid_bid(uid, current_user.id) # uid=sid, bid=current_user.id
    got_any_reviews=True
    already_reviewed = Seller.already_reviewed(uid, current_user.id)
    if request.method == 'POST':
        if current_user.is_authenticated:
            upvote_receiver_uid = request.form.get('receiver_uid') # whose review was upvoted?
            if request.form.get('upvote') != None:  # is an upvote request
                upvote_receiver_uid = int(upvote_receiver_uid)
                # reviewer = current user, seller = uid, buyer = upvote receiver (for their review for seller)
                if Seller.already_upvoted_seller(current_user.id, uid, upvote_receiver_uid):# (reviewer_id, seller_id, buyer_id)
                    flash('Already upvoted this review!')
                    review_list = get_reviews_and_names("None", False, uid) # product name, is it for product?, seller id
                    reviews_and_names = review_list[0]
                    if reviews_and_names==[]:
                        got_any_reviews=False
                    return render_template("seller_reviews.html",
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid, 
                           reviewer_uid=reviewer_uid,bought_from_this_seller=bought_from_this_seller,
                           already_reviewed=already_reviewed, seller_id=uid, got_any_reviews=got_any_reviews, this_user_review=review_list[1])
                # else add the upvote to upvote_receiver_uid

                current_upvotes = Seller.get_current_upvotes(uid, upvote_receiver_uid)['current_upvotes']
                result = Seller.add_upvote(uid, upvote_receiver_uid, current_upvotes) # (sid, bid, current_upvotes)
                result2 = Seller.record_upvote(current_user.id, uid, upvote_receiver_uid) # (reviewer_id, seller_id, buyer_id)
                flash('Review upvoted!')
                review_list = get_reviews_and_names("None", False, uid) # product name, is it for product?, seller id
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False

                return render_template("seller_reviews.html",
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid, 
                           reviewer_uid=reviewer_uid,bought_from_this_seller=bought_from_this_seller,
                           already_reviewed=already_reviewed, seller_id=uid,got_any_reviews=got_any_reviews, this_user_review=review_list[1])
            # if not upvote, then it's a review post request
            reviewer_uid = current_user.id
            if already_reviewed:
                flash('Already reviewed this seller!')
                review_list = get_reviews_and_names("None", False, uid) # product name, is it for product?, seller id
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False
                return render_template("seller_reviews.html",
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid, 
                           reviewer_uid=reviewer_uid,bought_from_this_seller=bought_from_this_seller,
                           already_reviewed=already_reviewed, seller_id=uid,got_any_reviews=got_any_reviews, this_user_review=review_list[1])
            else:
                review = request.form.get('review')
                result = Seller.add_review(uid, current_user.id, review)  #(seller_id, buyer_id, review)
                flash('Review added successfully!')
                review_list = get_reviews_and_names("None", False, uid) # product name, is it for product?, seller id
                reviews_and_names = review_list[0]
                if reviews_and_names==[]:
                    got_any_reviews=False
                return render_template("seller_reviews.html",
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=upvote_receiver_uid, 
                           reviewer_uid=reviewer_uid,bought_from_this_seller=bought_from_this_seller,
                           already_reviewed=already_reviewed, seller_id=uid,got_any_reviews=got_any_reviews, this_user_review=review_list[1])
    else:
        review_list = get_reviews_and_names("None", False, uid) # product name, is it for product?, seller id
        reviews_and_names = review_list[0]
        if reviews_and_names==[]:
            got_any_reviews=False
        return render_template("seller_reviews.html",
                           reviews_and_names=reviews_and_names, upvote_receiver_uid=None, 
                           reviewer_uid=None,bought_from_this_seller=bought_from_this_seller,
                           already_reviewed=already_reviewed, seller_id=uid,got_any_reviews=got_any_reviews, this_user_review=review_list[1])
