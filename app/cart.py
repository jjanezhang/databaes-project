from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from .models.cart import Cart

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/add_product', methods=['POST'])
def add_product():
    print(request.form)
    pid = request.form['pid']
    sid = request.form['seller']
    quantity = request.form['quantity']
    if current_user.is_authenticated:
        if Cart.add_item_to_cart(current_user.id, pid, sid, quantity) == 1:
            flash('Item successfully added to cart!')
        else:
            flash('Item already in cart')
    return redirect(request.referrer)
    