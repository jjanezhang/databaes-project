from datetime import datetime
from flask import current_app as app

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
            ORDER BY P.id
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
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid, quantity=quantity)
        return result

    @staticmethod
    # Remove an item from a user's inventory
    def remove_item(uid, pid):
        result = app.db.execute('''
            DELETE FROM Inventory
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)
        return result
    
    @staticmethod
    # Get items which have been sold the most by this seller after start_time
    def get_most_popular_items(uid, start_time=None):
        if not start_time:
            start_time = datetime(1980, 9, 14, 0, 0, 0)
        result = app.db.execute('''
            WITH TopPids AS (
                SELECT P.pid AS pid, sum(quantity) AS quantity
                FROM Purchases P, Orders O
                WHERE P.sid = :uid AND O.id = P.oid AND O.time_placed >= :start_time
                GROUP BY P.pid
                LIMIT 5
            )
            SELECT P.name AS name, P.id AS pid, T.quantity AS quantity
            FROM TopPids T, Products P
            WHERE T.pid = P.id
            ORDER BY quantity DESC
        ''', uid=uid, start_time=start_time)

        return [{"name": row.name, "pid": row.pid, "quantity_sold": row.quantity} for row in result]

    @staticmethod
    def get_inventory_stats(uid):
        result = app.db.execute('''
            SELECT count(*) as count, sum(quantity) as total, 
                avg(quantity) as avg, min(quantity) as min, max(quantity) as max
            FROM Inventory
            GROUP BY uid
            HAVING uid = :uid
        ''', uid=uid)

        return [{"count": row.count, "total": row.total, "avg": row.avg, "min": row.min, "max": row.max} for row in result][0]

    @staticmethod
    def get_n_fewest_items_in_inventory(uid, n):
        result = app.db.execute('''
            SELECT I.pid AS pid, P.name AS name, I.quantity AS quantity
            FROM Inventory I, Products P
            WHERE I.pid = P.id AND uid = :uid
            ORDER BY quantity ASC, P.id ASC
            LIMIT :n
        ''', uid=uid, n=n)

        return [{"pid": row.pid, "name": row.name, "quantity": row.quantity} for row in result]
