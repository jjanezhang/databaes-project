from flask import current_app as app
import sys

class Inventory:
    def __init__(self, uid, pid, name, quantity):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.quantity = quantity

    @staticmethod
    # Get all items from a user's inventory
    def get_all(uid):
        rows = app.db.execute('''
            SELECT I.uid AS uid, I.pid AS pid, P.name AS name, I.quantity AS quantity
            FROM Inventory I, Products P
            WHERE I.pid = P.id AND I.uid = :uid
        ''', uid=uid)
        return [Inventory(*row) for row in rows]

    @staticmethod
    # Add an item to a user's inventory
    def add_item(uid, pid, quantity):
        result = app.db.execute('''
            INSERT INTO Inventory(uid, pid, quantity)
            VALUES(:uid, :pid, :quantity)
        ''', uid=uid, pid=pid, quantity=quantity)
        return result

    @staticmethod
    # Update the quantity of an item in a user's inventory
    def update_item_quantity(uid, pid, quantity):
        result = app.db.execute('''
            UPDATE Inventory SET quantity = :quantity
            WHERE uid = :uid and pid = :pid
        ''', uid=uid, pid=pid, quantity=quantity)
        return result