from flask import Blueprint, current_app as app, render_template
from flask_login import current_user

from .models.inventory import Inventory

bp = Blueprint('inventory_stats', __name__, url_prefix='/inventory_stats')

@bp.route('/')
def index():
    if current_user.is_authenticated:
        most_popular_all_time = Inventory.get_most_popular_items_all_time(current_user.id)
    else:
        most_popular_all_time = None
    return render_template('inventory_stats.html', 
                            most_popular_all_time = most_popular_all_time)
