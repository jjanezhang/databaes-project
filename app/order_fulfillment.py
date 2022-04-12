import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from .models.order import Order
from .models.purchase import Purchase

bp = Blueprint('order_fulfillment', __name__, url_prefix='/order_fulfillment')

error = None

@bp.route('/seller')
def seller():
    global error
    if error:
        flash(error)
        error = None
    if current_user.is_authenticated:
        orders = Order.get_all_orders_for_seller(current_user.id)
        orderStats = list(map(lambda order: { "total_items": len(order.purchases),
            "fulfilled_items": len(list(filter(lambda x: x.fulfilled, order.purchases))), 
            "is_fulfilled": len(order.purchases) ==  len(list(filter(lambda x: x.fulfilled, order.purchases)))}, orders))
        orderInfo = list(map(lambda index: {"order": orders[index], "orderStats": orderStats[index]}, range(len(orders))))
        noOrders = len(orders) == 0
    else:
        orders = None
        orderStats = None
        orderInfo = None
    return render_template('order_fulfillment_seller.html', 
                            orderInfo = orderInfo,
                            noOrders = noOrders)

@bp.route('/seller/fulfill_purchase', methods=['POST'])
def fulfill_purchase():
    if current_user.is_authenticated:
        result = Order.fulfill_purchase(request.form['oid'], request.form['pid'], current_user.id)
        if result != 1:
            global error
            error = "Unable to fulfill purchase. You do not have enough items in your inventory."
    return redirect(url_for('order_fulfillment.seller'))

@bp.route('buyer')
def buyer_history():
    if current_user.is_authenticated:
        # find the products current user has bought:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        orders = Order.get_all_orders_for_buyer(current_user.id)
        orderStats = list(map(lambda order: { "total_items": len(order.purchases),
                "fulfilled_items": len(list(filter(lambda x: x.fulfilled, order.purchases))), 
                "is_fulfilled": len(order.purchases) ==  len(list(filter(lambda x: x.fulfilled, order.purchases))),
                "total_price": sum(map(lambda purchase: purchase.price * purchase.quantity, order.purchases))}, orders))
        all_order_info = list(map(lambda x: { "order": orders[x], "orderStats": orderStats[x] }, range(0, len(orders))))
    else:
        purchases = None
    return render_template('order_history.html', purchases=purchases, orderInfo=all_order_info)

@bp.route('buyer/<orderId>')
def buyer(orderId):
    if current_user.is_authenticated:
        order = Order.get_order_for_buyer(orderId, current_user.id)
        if order is not None:
            orderStats = { "total_items": len(order.purchases),
                "fulfilled_items": len(list(filter(lambda x: x.fulfilled, order.purchases))), 
                "is_fulfilled": len(order.purchases) ==  len(list(filter(lambda x: x.fulfilled, order.purchases))),
                "total_price": sum(map(lambda purchase: purchase.price * purchase.quantity, order.purchases))}
        else:
            orderStats = None
    else:
        order = None
        orderStats = None
    return render_template('order_fulfillment_buyer.html', 
                            order = order,
                            orderStats = orderStats)
