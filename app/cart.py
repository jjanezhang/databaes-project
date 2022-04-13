from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired


from .models.cart import Cart

bp = Blueprint('cart', __name__, url_prefix='/cart')


class QuantityForm(FlaskForm):
    pid = SelectField('Product Name', validators=[DataRequired()])
    sid = SelectField('Seller Name', validators=[DataRequired()])
    new_quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField('Update Quantity')


class SubmitCartForm(FlaskForm):
    submit = SubmitField('Submit Order')


@bp.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        cart = Cart.get_cart(current_user.id)
        totalPrice = sum(map(lambda x: x.quantity * x.price, cart))
        quantity_form = QuantityForm()
        quantity_form.pid.choices = [(item.pid, item.product_name) for item in cart]
        quantity_form.sid.choices = [(item.sid, item.seller_name) for item in cart]
        submit_cart_form = SubmitCartForm()
        if quantity_form.validate_on_submit():
            update = Cart.update_item_quantity(current_user.id, quantity_form.pid.data, quantity_form.sid.data, quantity_form.new_quantity.data)
            if update == 1:
                return redirect(url_for('cart.index'))
            else:
                flash(update)
    else:
        cart = None
        totalPrice = 0
        quantity_form = None
        submit_cart_form = None
    return render_template('cart.html', cart=cart, totalPrice=totalPrice, quantity_form=quantity_form, submit_cart_form=submit_cart_form)


@bp.route('/add_product', methods=['POST'])
def add_product():
    pid = request.form['pid']
    sid = request.form['seller']
    quantity = request.form['quantity']
    if current_user.is_authenticated:
        result = Cart.add_item_to_cart(current_user.id, pid, sid, quantity)
        if result == 1:
            flash('Item successfully added to cart!')
        else:
            flash(result)
    return redirect(request.referrer)


@bp.route('/remove_product', methods=['POST'])
def remove_product():
    if current_user.is_authenticated:
        Cart.remove_item_from_cart(current_user.id, request.form['pid'], request.form['sid'])
    return redirect(url_for('cart.index'))


@bp.route('/submit', methods=['POST'])
def submit():
    if current_user.is_authenticated:
        result = Cart.submit(current_user.id)
        if result != 1:
            flash(result)
        else:
            flash("Order successfully submitted!")
    return redirect(url_for('cart.index'))
