from flask import current_app as app

from app.models.purchase import Purchase

class Order:
    def __init__(self, oid, uid, time_placed):
        self.oid = oid
        self.uid = uid
        self.time_placed = time_placed

    @staticmethod
    # Get all orders for a seller where at least one item in the order is unfulfilled
    def get_all_unfulfilled_orders_for_seller(uid):
        rows = app.db.execute('''
            SELECT O.id AS oid, O.uid as uid, O.time_placed AS time_placed, P.pid AS pid, 
            P.fulfilled AS fulfilled, P.time_fulfilled AS time_fulfilled, P.price AS price, Pr.name AS product_name
            FROM Orders O, Purchases P, Product Pr
            WHERE O.id = P.oid AND P.sid = :uid AND Pr.id = P.pid AND EXISTS (
                SELECT *
                FROM Purchases P2
                WHERE P2.oid = P.oid AND P2.sid = :uid AND P2.fulfilled = FALSE
            )
            ORDER BY O.time_placed DESC
        ''', uid=uid)
        result = {}
        for row in rows:
            if row.oid in result:
                result[row.oid].append(Purchase(row.oid, row.pid, uid, row.fulfilled, row.time_fulfilled, row.price, row.product_name))
            else:
                result[row.oid] = Order(row.oid, row.uid, row.time_placed)
                result[row.oid].purchases.append(Purchase(row.oid, row.pid, uid, row.fulfilled, row.time_fulfilled, row.price, row.product_name))
        return list(result.values())
