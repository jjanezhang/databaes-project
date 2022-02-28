from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

import datetime
import sys

from .models.inventory import Inventory
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

class QuantityForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Quantity')

@bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    quantity_form = QuantityForm()
    if current_user.is_authenticated:
        inventory = Inventory.get_all(current_user.id)
        quantity_form.pid.choices = [(product.pid, product.name) for product in inventory]
        quantity_form.pid.choices.sort()
        if quantity_form.validate_on_submit():
            if Inventory.update_item_quantity(current_user.id, quantity_form.pid.data, quantity_form.quantity.data):
                return redirect(url_for('index.inventory'))
    else:
        inventory = None
    return render_template('inventory.html', 
                            inventory=inventory,
                            quantity_form=quantity_form)