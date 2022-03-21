from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from .models.order import Order

bp = Blueprint('order_fulfillment', __name__, url_prefix='/order_fulfillment')

error = None

@bp.route('/')
def index():
    global error
    if error:
        flash(error)
        error = None
    if current_user.is_authenticated:
        orders = Order.get_all_unfulfilled_orders_for_seller(current_user.id)
        orderStats = list(map(lambda order: { "total_items": len(order.purchases),
            "fulfilled_items": len(list(filter(lambda x: x.fulfilled, order.purchases))) }, orders))
        orderInfo = list(map(lambda index: {"order": orders[index], "orderStats": orderStats[index]}, range(len(orders))))
        no_orders = len(orderInfo) == 0
    else:
        orders = None
        orderStats = None
        orderInfo = None
    return render_template('order_fulfillment.html', 
                            orderInfo = orderInfo,
                            no_orders = no_orders)

@bp.route('/fulfill_purchase', methods=['POST'])
def fulfill_purchase():
    if current_user.is_authenticated:
        result = Order.fulfill_purchase(request.form['oid'], request.form['pid'], current_user.id, request.form['quantity'])
        if result != 1:
            global error
            error = "Unable to fulfill purchase. You do not have enough items in your inventory."
    return redirect(url_for('order_fulfillment.index'))