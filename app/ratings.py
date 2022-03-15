from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from .models.inventory import Inventory
from .models.product import Product

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

class RatingsForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_rating = IntegerField('Rating', validators=[InputRequired(), NumberRange(min=0, max=5)])
    submit = SubmitField('Update Rating')

def getTemplateVariables(since):
    ratings_form = RatingsForm()
    uid = current_user.id
    since = now() - 90 # check back up to 90 days behind in time
    if current_user.is_authenticated:
        all_purchases = Purchase.get(uid) # get all items purchased by this user
        all_products = Product.get_all_regardless_of_availability()
        products_to_rate = []  # want the name and pid of the products
        for i in range(len(all_purchases)):
            for j in range(len(all_products)):
                if all_purchases[i].id = all_products[j].id:
                    products_to_rate.append( (all_products.name, all_products.id) )

        ratings_form.pid.choices = products_to_rate # [(product.pid, product.name) for product in purchases]
        ratings_form.pid.choices.sort()
        #all_products = filter(lambda product: product.id not in [x.pid for x in inventory], all_products)
        #add_product_form.pid.choices = [(product.id, product.name) for product in all_products]
        #add_product_form.pid.choices.sort()
    else:
        all_purchases = None
    return (all_purchases, ratings_form) #, add_product_form)

@bp.route('/')
def index():
    (inventory, ratings_form) = getTemplateVariables()
    return render_template('ratings.html', 
                            inventory=inventory,
                            ratings_form=ratings_form)

@bp.route('/update_rating', methods=['POST'])
def update_rating():
    (inventory, ratings_form) = getTemplateVariables()
    if current_user.is_authenticated and ratings_form.validate_on_submit():
        if Inventory.add_item(current_user.id, add_product_form.pid.data, add_product_form.quantity.data):
            return redirect(url_for('inventory.index'))
    return render_template('inventory.html', 
                            inventory=inventory,
                            add_product_form=add_product_form,
                            quantity_form=quantity_form)