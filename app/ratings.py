from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from .models.rated import Rated
from .models.product import Product
from .models.purchase import Purchase
from datetime import timedelta
import datetime

bp = Blueprint('ratings', __name__, url_prefix='/ratings')

class RatingsForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Update Rating')

class AddRatingForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Add Rating')

def getTemplateVariables():
    ratings_form = RatingsForm()    # create a new form using which we can add an item to rate
    add_rating_form = AddRatingForm()
    #since = datetime.today() - timedelta(days=90) # check up to 90 days behind in time
    since = datetime.datetime(1980, 9, 14, 0, 0, 0)
    if current_user.is_authenticated:
        rated_products = Rated.get_all(current_user.id)
        ratings_form.pid.choices = [(product.pid, product.name) for product in rated_products]
        ratings_form.pid.choices.sort()

        all_user_purchases = Purchase.get_all_by_uid_since(current_user.id, since) # get all items purchased by this user
        all_products = Product.get_all_regardless_of_availability() #
        purchased_products = filter(lambda product: product.id in [x.pid for x in all_user_purchases], all_products)
        # ratings_form.pid.choices = [(product.id, product.name) for product in purchased_products]

        add_rating_form.pid.choices = [(product.id, product.name) for product in purchased_products]
        add_rating_form.pid.choices.sort()
    else:
        rated_products = None
    return (rated_products, ratings_form, add_rating_form) 

@bp.route('/')
def index():
    (purchased_products, ratings_form, add_rating_form) = getTemplateVariables()
    # if current_user.is_authenticated:
    #     if current_user.id ==2:
    #         return render_template('test.html')
    return render_template('ratings.html', 
                            purchased_products=purchased_products,
                            ratings_form=ratings_form,
                            add_rating_form=add_rating_form)

@bp.route('/update_rating', methods=['POST'])
def update_rating():
    (purchased_products, ratings_form, add_rating_form) = getTemplateVariables()
    if current_user.is_authenticated and add_rating_form.validate_on_submit():
        if Rated.update_rating(current_user.id, ratings_form.pid.data, ratings_form.new_rating.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html', 
                            purchased_products=purchased_products,
                            ratings_form=ratings_form,
                            add_rating_form=add_rating_form)

@bp.route('/add_rating', methods=['POST'])
def add_rating():
    (purchased_products, ratings_form, add_rating_form) = getTemplateVariables()
    if current_user.is_authenticated and add_rating_form.validate_on_submit():
        if Rated.add_rating(current_user.id, ratings_form.pid.data, ratings_form.new_rating.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html', 
                            purchased_products=purchased_products,
                            ratings_form=ratings_form,
                            add_rating_form=add_rating_form)

@bp.route('/remove_rating', methods=['POST'])
def remove_rating():
    if current_user.is_authenticated:
        Rated.remove_rating(current_user.id, request.form['pid'])
    return redirect(url_for('ratings.index'))