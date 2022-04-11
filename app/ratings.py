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
    ratings_form = RatingsForm() 
    # add_rating_form = AddRatingForm()
    since = datetime.datetime(1980, 9, 14, 0, 0, 0)

    if current_user.is_authenticated:
        rated_products = Rated.get_all_by_uid(current_user.id)
        print("rated products for this user: ", rated_products)
        ratings_form.pid.choices = [(product.pid, product.name) for product in rated_products] 
        # already sorted by time_added, above
        return (rated_products, ratings_form) 
    else:
        rated_products = None
        return ([], ratings_form)

@bp.route('/')
def index():
    (rated_products, ratings_form) = getTemplateVariables()
    return render_template('ratings.html', 
                            rated_products=rated_products,
                            ratings_form=ratings_form)

@bp.route('/update_rating', methods=['POST'])
def update_rating():
    (rated_products, ratings_form) = getTemplateVariables()
    if current_user.is_authenticated and ratings_form.validate_on_submit():
        if Rated.update_rating(current_user.id, ratings_form.pid.data, ratings_form.new_rating.data):
            return redirect(url_for('ratings.index'))
    return render_template('ratings.html', 
                            rated_products=rated_products,
                            ratings_form=ratings_form)

@bp.route('/remove_rating', methods=['POST'])
def remove_rating():
    if current_user.is_authenticated:
        Rated.remove_rating(current_user.id, request.form['pid'])
    return redirect(url_for('ratings.index'))