from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_all_regardless_of_availability():
        rows = app.db.execute('''
            SELECT id, name, price, available
            FROM Products
            ''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_product_by_name(product_name):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE name = :product_name
''',
                              product_name=product_name)
        if len(rows) ==0:
            return [None]
        return [Product(*row) for row in rows]

    @staticmethod
    def get_sellers_and_quantities_for_product(product_name):
        rows = app.db.execute('''
            SELECT I.pid AS pid, U.firstname AS firstname, U.lastname AS lastname, I.quantity AS quantity
            FROM Inventory I, Products P, Users U
            WHERE I.pid = P.id AND U.id = I.uid AND I.quantity > 0 AND P.name = :product_name
            ''', product_name=product_name)
        return [{'pid': row['pid'], 'firstname': row['firstname'], 'lastname': row['lastname'], 'quantity': row['quantity']} for row in rows]