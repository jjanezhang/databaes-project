from datetime import datetime, timezone
from flask import current_app as app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.models.purchase import Purchase
from app.models.user import User

class Order:
    def __init__(self, oid, uid, time_placed, purchases=[], buyer=None):
        self.oid = oid
        self.uid = uid
        self.time_placed = time_placed
        self.purchases = purchases if purchases else []
        # buyer is the User object that corresponds to uid
        self.buyer = buyer if buyer else None

    @staticmethod
    # Get all orders for a seller
    def get_all_orders_for_seller(uid):
        rows = app.db.execute('''
            SELECT O.id AS oid, O.uid as uid, O.time_placed AS time_placed, P.pid AS pid, 
            P.fulfilled AS fulfilled, P.time_fulfilled AS time_fulfilled, 
            P.quantity AS quantity, P.price AS price, Pr.name AS product_name
            FROM Orders O, Purchases P, Products Pr
            WHERE O.id = P.oid AND P.sid = :uid AND Pr.id = P.pid
            ORDER BY O.time_placed DESC
        ''', uid=uid)
        result = {}
        for row in rows:
            if row.oid in result:
                result[row.oid].purchases.append(Purchase(row.oid, row.pid, uid, row.fulfilled, row.time_fulfilled, row.quantity, row.price, row.product_name, row.time_placed))
            else:
                result[row.oid] = Order(row.oid, row.uid, row.time_placed)
                result[row.oid].purchases.append(Purchase(row.oid, row.pid, uid, row.fulfilled, row.time_fulfilled, row.quantity, row.price, row.product_name, row.time_placed))

        for key in result:
            result[key].buyer = User.get(result[key].uid)

        return list(result.values())

    @staticmethod
    # Fulfill a purchase as part of order 'oid' for product 'pid' sold by seller 'sid'
    def fulfill_purchase(oid, pid, sid):
        current_timestamp = datetime.now(timezone.utc)
        result = app.db.execute('''
            UPDATE Purchases SET fulfilled = TRUE, time_fulfilled = :current_timestamp
            WHERE oid = :oid AND pid = :pid AND sid = :sid
        ''', current_timestamp=current_timestamp, oid=oid, pid=pid, sid=sid)
        return result

    @staticmethod
    # Get a specific order for a buyer
    def get_order_for_buyer(oid, uid):
        rows = app.db.execute('''
            SELECT O.id AS oid, O.uid AS uid, O.time_placed AS time_placed, P.sid AS sid, P.pid AS pid, 
            P.fulfilled AS fulfilled, P.time_fulfilled AS time_fulfilled, 
            P.quantity AS quantity, P.price AS price, Pr.name AS product_name
            FROM Orders O, Purchases P, Products Pr
            WHERE O.id = :oid AND uid = :uid AND O.id = P.oid AND O.uid = :uid AND Pr.id = P.pid
        ''', oid=oid, uid=uid)

        if len(rows) > 0:
            result = Order(rows[0].oid, uid, rows[0].time_placed)
            for row in rows:
                result.purchases.append(Purchase(row.oid, row.pid, row.sid, row.fulfilled, row.time_fulfilled, row.quantity, row.price, row.product_name, row.time_placed))
            user = User.get(uid)
            result.buyer = user
            return result
        else:
            return None
