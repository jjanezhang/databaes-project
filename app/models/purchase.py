from flask import current_app as app


class Purchase:
    def __init__(self, oid, pid, sid, fulfilled, time_fulfilled, quantity, price, product_name, time_purchased):
        self.oid = oid
        self.pid = pid
        self.sid = sid
        self.fulfilled = fulfilled
        self.time_fulfilled = time_fulfilled
        self.quantity = quantity
        self.price = price
        self.product_name = product_name
        self.time_purchased = time_purchased

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
            SELECT P.oid AS oid, P.pid AS pid, P.sid AS sid, P.fulfilled AS fulfilled,
            P.time_fulfilled AS time_fulfilled, P.quantity AS quantity,
            P.price AS price, Pr.name AS product_name, O.time_placed AS time_purchased
            FROM Purchases P, Orders O, Products Pr
            WHERE O.id = P.oid AND O.uid = :uid AND P.pid = Pr.id
            AND O.time_placed >= :since
            ORDER BY O.time_placed DESC
            '''
        , uid=uid, since=since)
        return [Purchase(*row) for row in rows]