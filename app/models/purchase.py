from flask import current_app as app


class Purchase:
    def __init__(self, oid, pid, sid, fulfilled, time_fulfilled, quantity,
                 price, product_name, time_purchased, seller_name):
        self.oid = oid
        self.pid = pid
        self.sid = sid
        self.fulfilled = fulfilled
        self.time_fulfilled = time_fulfilled
        self.quantity = quantity
        self.price = price
        self.product_name = product_name
        self.time_purchased = time_purchased
        self.seller_name = seller_name

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
            SELECT P.oid AS oid, P.pid AS pid, P.sid AS sid, P.fulfilled AS fulfilled,
            P.time_fulfilled AS time_fulfilled, P.quantity AS quantity,
            P.price AS price, Pr.name AS product_name, O.time_placed AS time_purchased,
            CONCAT(U.firstname, ' ', U.lastname) AS seller_name
            FROM Purchases P, Orders O, Products Pr, Users U
            WHERE O.id = P.oid AND O.uid = :uid AND P.pid = Pr.id AND U.id = P.sid
            AND O.time_placed >= :since
            ORDER BY O.time_placed DESC
            ''', uid=uid, since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_product_by_uid_pid(uid, product_id):
        rows = app.db.execute('''
            SELECT P.oid AS oid, P.pid AS pid, P.sid AS sid, P.fulfilled AS fulfilled,
            P.time_fulfilled AS time_fulfilled, P.quantity AS quantity,
            P.price AS price, Pr.name AS product_name, O.time_placed AS time_purchased,
            CONCAT(firstname, ' ', lastname) AS seller_name
            FROM Purchases P, Orders O, Products Pr, Users U
            WHERE O.id = P.oid AND O.uid = :uid AND P.pid = :product_id AND U.id = P.sid
            AND P.pid = Pr.id AND P.fulfilled=true
            ''', uid=uid, product_id=product_id)

        # print("what is this even returning? ", [row for row in rows])
        rowcount = len(rows)
        if rowcount > 0:
            ret = [True]
            purchase = [Purchase(*row) for row in rows]
            ret += purchase
            return ret

        else:
            ret = [False]
            return ret
        
    @staticmethod
    # TODO: AND P.fulfilled=true ?????
    def check_purchased_by_uid_pid(uid, pid):
        rows = app.db.execute('''
            SELECT P.oid AS oid
            FROM Purchases P, Orders O
            WHERE O.uid = :uid AND P.pid = :pid AND O.id = P.oid
            ''', uid=uid, pid=pid)

        print("is this product purchased? ", [r for r in rows])
        result = [r for r in rows]
        if len(result)>0:
            return True
        return False

        return True
