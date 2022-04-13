from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template

from flask_login import current_user

from .models.inventory import Inventory

bp = Blueprint('inventory_and_order_stats', __name__,
               url_prefix='/inventory_and_order_stats')


@bp.route('/')
def index():
    if current_user.is_authenticated:
        most_popular_all_time = Inventory.get_most_popular_items(
            current_user.id)
        most_popular_last_month = Inventory.get_most_popular_items(
            current_user.id, datetime.now(timezone.utc) - relativedelta(months=1))
        most_popular_last_week = Inventory.get_most_popular_items(
            current_user.id, datetime.now(timezone.utc) - relativedelta(weeks=1))
        inventory_stats = Inventory.get_inventory_stats(current_user.id)
        inventory_low_items = Inventory.get_n_fewest_items_in_inventory(
            current_user.id, 5)
    else:
        most_popular_all_time = None
        most_popular_last_month = None
        most_popular_last_week = None
        inventory_stats = None
        inventory_low_items = None
    return render_template('inventory_and_order_stats.html',
                           most_popular_all_time=most_popular_all_time,
                           most_popular_last_month=most_popular_last_month,
                           most_popular_last_week=most_popular_last_week,
                           inventory_stats=inventory_stats,
                           inventory_low_items=inventory_low_items)
