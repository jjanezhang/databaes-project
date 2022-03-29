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
    # Get items which have been sold the most by this seller all time
    def get_most_popular_items_all_time(uid):
        result = app.db.execute('''
            WITH TopPids AS (SELECT P.pid AS pid, sum(quantity) AS quantity
            FROM Purchases P
            WHERE P.sid = :uid
            GROUP BY P.pid
            LIMIT 5)
            SELECT P.name AS name, P.id AS pid, T.quantity AS quantity
            FROM TopPids T, Products P
            WHERE T.pid = P.id
            ORDER BY quantity DESC
        ''', uid=uid)

        return [{"name": row.name, "pid": row.pid, "quantity_sold": row.quantity} for row in result]
