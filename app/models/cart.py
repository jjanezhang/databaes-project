from datetime import datetime, timezone
from flask import current_app as app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.models.purchase import Purchase
from app.models.user import User

class CartItem:
    def __init__(self, pid, sid, quantity):
        self.pid = pid
        self.sid = sid
        self.quantity = quantity

class Cart:
    def __init__(self, cartItems = []):
        self.cartItems = cartItems

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
            print(e)
            return 'Item already in cart.'
        return result.rowcount

    @staticmethod
    def get_cart(uid):
        rows = app.db.execute('''
            SELECT pid, sid, quantity
            FROM Cart
            WHERE uid = :uid
        ''', uid=uid)
        cart = Cart()
        for row in rows:
            cart.cartItems.append(CartItem(row['pid'], row['sid'], row['quantity']))
        return cart

