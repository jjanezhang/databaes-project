from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from .models.rated import Rated
from .models.seller import Seller
import datetime

bp = Blueprint('ratings', __name__, url_prefix='/ratings')


class RatingsForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Update Rating')

class ReviewsProductsForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_review = TextAreaField('Review for product', validators=[DataRequired()])
    submit = SubmitField('Update Review')

class ReviewsSellersForm(FlaskForm):
    sid = SelectField('Seller Name', validators=[DataRequired()])
    new_seller_review = TextAreaField('Review for seller', validators=[DataRequired()])
    submit = SubmitField('Update Review')

class SellerRatingsForm(FlaskForm):
    sid = SelectField('Seller Name', validators=[DataRequired()])
    new_seller_rating = IntegerField('Rating for seller', validators=[InputRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Update Rating')

class AddRatingForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Add Rating')

def getTemplateVariables():
    ratings_form = RatingsForm()
    reviews_product_form = ReviewsProductsForm()
    reviews_seller_form =ReviewsSellersForm()
    seller_ratings_form =SellerRatingsForm()
    if current_user.is_authenticated:
        rated_products = Rated.get_all_by_uid(current_user.id)
        ratings_form.pid.choices = [(product.pid, product.name) for product in rated_products] # already sorted by time_added, above
        reviews_product_form.pid.choices = ratings_form.pid.choices  #[(product.pid, product.name) for product in rated_products]
        
        rated_sellers = Seller.get_all_by_bid(current_user.id)
        seller_ratings_form.sid.choices =[(seller.sid, seller.name) for seller in rated_sellers]
        reviews_seller_form.sid.choices = seller_ratings_form.sid.choices
        return (rated_products, ratings_form, reviews_product_form,
        reviews_seller_form, seller_ratings_form,rated_sellers) 
    else:
        rated_products = None
        return ([], ratings_form, reviews_product_form,
        reviews_seller_form, seller_ratings_form,[])


@bp.route('/')
def index():
    (rated_products, ratings_form, reviews_product_form,reviews_seller_form, seller_ratings_form,rated_sellers) = getTemplateVariables()
    return render_template('ratings.html',
                            rated_products=rated_products,
                            ratings_form=ratings_form,
                            reviews_product_form=reviews_product_form,
                            reviews_seller_form=reviews_seller_form,
                            seller_ratings_form=seller_ratings_form,
                            rated_sellers=rated_sellers)


@bp.route('/update_rating', methods=['POST'])
def update_rating():
    (rated_products, ratings_form, reviews_product_form,reviews_seller_form, seller_ratings_form,rated_sellers) = getTemplateVariables()
    if current_user.is_authenticated and ratings_form.validate_on_submit():
        if Rated.update_rating(current_user.id, ratings_form.pid.data, ratings_form.new_rating.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html',
                            rated_products=rated_products,
                            ratings_form=ratings_form,
                            reviews_product_form=reviews_product_form,
                            reviews_seller_form=reviews_seller_form,
                            seller_ratings_form=seller_ratings_form,
                            rated_sellers=rated_sellers)

@bp.route('/update_review', methods=['POST'])
def update_review():
    (rated_products, ratings_form, reviews_product_form,reviews_seller_form, seller_ratings_form,rated_sellers) = getTemplateVariables()
    if current_user.is_authenticated and reviews_product_form.validate_on_submit():
        if Rated.update_review(current_user.id, reviews_product_form.pid.data, reviews_product_form.new_review.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html',
                            rated_products=rated_products,
                            ratings_form=ratings_form,
                            reviews_product_form=reviews_product_form,
                            reviews_seller_form=reviews_seller_form,
                            seller_ratings_form=seller_ratings_form,
                            rated_sellers=rated_sellers)

@bp.route('/update_seller_rating', methods=['POST'])
def update_seller_rating():
    (rated_products, ratings_form, reviews_product_form,reviews_seller_form, seller_ratings_form,rated_sellers) = getTemplateVariables()
    if current_user.is_authenticated and seller_ratings_form.validate_on_submit():
        if Seller.update_rating(current_user.id, seller_ratings_form.sid.data, seller_ratings_form.new_seller_rating.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html',
                            rated_products=rated_products,
                            ratings_form=ratings_form,
                            reviews_product_form=reviews_product_form,
                            reviews_seller_form=reviews_seller_form,
                            seller_ratings_form=seller_ratings_form,
                            rated_sellers=rated_sellers)

@bp.route('/update_seller_review', methods=['POST'])
def update_seller_review():
    (rated_products, ratings_form, reviews_product_form,reviews_seller_form, seller_ratings_form,rated_sellers) = getTemplateVariables()
    if current_user.is_authenticated and reviews_seller_form.validate_on_submit():
        if Seller.update_review(current_user.id, reviews_seller_form.sid.data, reviews_seller_form.new_seller_review.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html',
                            rated_products=rated_products,
                            ratings_form=ratings_form,
                            reviews_product_form=reviews_product_form,
                            reviews_seller_form=reviews_seller_form,
                            seller_ratings_form=seller_ratings_form,
                            rated_sellers=rated_sellers)

@bp.route('/remove_rating', methods=['POST'])
def remove_rating():
    if current_user.is_authenticated:
        Rated.remove_rating(current_user.id, request.form['pid'])
    return redirect(url_for('ratings.index'))

@bp.route('/remove_review', methods=['POST'])
def remove_review():
    if current_user.is_authenticated:
        Rated.remove_review(current_user.id, request.form['pid'])
    return redirect(url_for('ratings.index'))


@bp.route('/remove_seller_rating', methods=['POST'])
def remove_seller_rating():
    if current_user.is_authenticated:
        print("request.form.get('sid'): ", )
        Seller.remove_rating(current_user.id,request.form.get('sid'))
    return redirect(url_for('ratings.index'))

@bp.route('/remove_seller_review', methods=['POST'])
def remove_seller_review():
    if current_user.is_authenticated:
        Seller.remove_review(current_user.id,request.form.get('sid'))
    return redirect(url_for('ratings.index'))
