from flask import current_app as app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class CartItem:
    def __init__(self, pid, sid, product_name, seller_name, quantity, price):
        self.pid = pid
        self.sid = sid
        self.product_name = product_name
        self.seller_name = seller_name
        self.quantity = quantity
        self.price = price


class Cart:
    @staticmethod
    def add_item_to_cart(uid, pid, sid, quantity):
        try:
            with app.db.engine.begin() as conn:
                seller_quantity = conn.execute(text('''
                    SELECT quantity
                    FROM Inventory
                    WHERE uid = :sid AND pid = :pid
                '''), sid=sid, pid=pid)
                seller_quantity = seller_quantity.fetchone()
                if len(seller_quantity) > 0 and int(quantity) <= seller_quantity[0]:
                    result = conn.execute(text('''
                        INSERT INTO Cart(uid, pid, sid, quantity)
                        VALUES(:uid, :pid, :sid, :quantity)
                    '''), uid=uid, pid=pid, sid=sid, quantity=quantity)
                else:
                    return 'Choose a lower quantity.'
        except SQLAlchemyError as e:
            return 'Item already in cart.'
        return result.rowcount

    @staticmethod
    def get_cart(uid):
        rows = app.db.execute('''
            SELECT C.pid AS pid,C.sid AS sid, C.quantity AS quantity, P.price AS price, P.name AS name,
            U.firstname AS firstname, U.lastname AS lastname
            FROM Cart C, Products P, Users U
            WHERE C.uid = :uid AND C.pid = P.id AND U.id = C.sid
        ''', uid=uid)
        result = []
        for row in rows:
            result.append(CartItem(row['pid'], row['sid'], row['name'],
                                   row['firstname'] + ' ' + row['lastname'],
                                   row['quantity'], row['price']))
        return result

    @staticmethod
    def remove_item_from_cart(uid, pid, sid):
        result = app.db.execute('''
            DELETE FROM Cart
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''', uid=uid, pid=pid, sid=sid)
        return result

    @staticmethod
    def update_item_quantity(uid, pid, sid, new_quantity):
        if(new_quantity <= 0):
            return 'Choose a quantity > 0.'
        try:
            with app.db.engine.begin() as conn:
                seller_quantity = conn.execute(text('''
                    SELECT quantity
                    FROM Inventory
                    WHERE uid = :sid AND pid = :pid
                '''), sid=sid, pid=pid)
                seller_quantity = seller_quantity.fetchone()
                if seller_quantity == None:
                    return 'Choose a valid item in your cart.'
                if len(seller_quantity) > 0 and int(new_quantity) <= seller_quantity[0]:
                    result = conn.execute(text('''
                        UPDATE Cart SET quantity = :new_quantity
                        WHERE uid = :uid AND pid = :pid AND sid = :sid
                    '''), uid=uid, pid=pid, sid=sid, new_quantity=new_quantity)
                else:
                    return 'Choose a lower quantity.'
        except SQLAlchemyError as e:
            return 'Unable to update cart.'
        return result.rowcount

    @staticmethod
    # Submit a user's cart and create a new order
    def submit(uid):
        try:
            with app.db.engine.begin() as conn:
                cart = Cart.get_cart(uid)
                totalPrice = sum(map(lambda x: x.quantity * x.price, cart))
                conn.execute(text('''
                    UPDATE Users SET balance = balance - :totalPrice
                    WHERE id = :uid
                '''), totalPrice=totalPrice, uid=uid)
                conn.execute(text('''
                    DELETE FROM Cart WHERE uid = :uid
                '''), uid=uid)
                conn.execute(text('''
                    INSERT INTO Orders(uid)
                    VALUES(:uid)
                '''), uid=uid)
                newOrder = conn.execute(text('''
                    SELECT max(id)
                    FROM Orders
                    WHERE uid = :uid
                '''), uid=uid)
                oid = newOrder.fetchone()[0]
                for item in cart:
                    conn.execute(text('''
                        UPDATE Inventory
                        SET quantity = quantity - :quantity
                        WHERE uid = :sid AND pid = :pid
                    '''), quantity=item.quantity, sid=item.sid, pid=item.pid)
                    conn.execute(text('''
                        INSERT INTO Purchases(oid, pid, sid, fulfilled, time_fulfilled, quantity, price)
                        VALUES(:oid, :pid, :sid, FALSE, NULL, :quantity, :price)
                    '''), oid=oid, pid=item.pid, sid=item.sid, quantity=item.quantity, price=item.price)
        except IntegrityError as e:
            if 'users_balance_check' in str(e):
                return "You do not have enough balance to complete this order."
            elif 'inventory_quantity_check' in str(e):
                error_pid = e.params['pid']
                error_product_name = next(
                    item for item in cart if item.pid == error_pid).product_name
                return f"There is no longer enough quantity of {error_product_name} to satisfy your purchase."
            else:
                return "Unable to complete your purchase"
        return 1
