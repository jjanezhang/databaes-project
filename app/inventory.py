from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from .models.inventory import Inventory
from .models.product import Product

bp = Blueprint('inventory', __name__, url_prefix='/inventory')


class QuantityForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    new_quantity = IntegerField('Quantity', validators=[
                                InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Quantity')


class AddProductForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
                            InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Product')


def getTemplateVariables():
    quantity_form = QuantityForm()
    add_product_form = AddProductForm()
    if current_user.is_authenticated:
        all_products = Product.get_all_regardless_of_availability()
        inventory = Inventory.get_all(current_user.id)
        quantity_form.pid.choices = [
            (product.pid, product.name) for product in inventory]
        quantity_form.pid.choices.sort()
        all_products = filter(lambda product: product.id not in [
                              x.pid for x in inventory], all_products)
        add_product_form.pid.choices = [
            (product.id, product.name) for product in all_products]
        add_product_form.pid.choices.sort()
    else:
        inventory = None
    return (inventory, quantity_form, add_product_form)


@bp.route('/')
def index():
    (inventory, quantity_form, add_product_form) = getTemplateVariables()
    return render_template('inventory.html',
                           inventory=inventory,
                           add_product_form=add_product_form,
                           quantity_form=quantity_form)


@bp.route('/add_product', methods=['POST'])
def add_product():
    (inventory, quantity_form, add_product_form) = getTemplateVariables()
    if current_user.is_authenticated and add_product_form.validate_on_submit():
        if Inventory.add_item(current_user.id, add_product_form.pid.data, add_product_form.quantity.data):
            return redirect(url_for('inventory.index'))
    return render_template('inventory.html',
                           inventory=inventory,
                           add_product_form=add_product_form,
                           quantity_form=quantity_form)


@bp.route('/update_quantity', methods=['POST'])
def update_quantity():
    (inventory, quantity_form, add_product_form) = getTemplateVariables()
    if current_user.is_authenticated and quantity_form.validate_on_submit():
        if Inventory.update_item_quantity(current_user.id, quantity_form.pid.data, quantity_form.new_quantity.data):
            return redirect(url_for('inventory.index'))
    return render_template('inventory.html',
                           inventory=inventory,
                           add_product_form=add_product_form,
                           quantity_form=quantity_form)


@bp.route('/remove_product', methods=['POST'])
def remove_product():
    if current_user.is_authenticated:
        Inventory.remove_item(current_user.id, request.form['pid'])
    return redirect(url_for('inventory.index'))
