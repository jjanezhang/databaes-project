from unittest import result
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class Product:
    def __init__(self, id, name, price, available, image_url):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.image_url = image_url

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available, image_url
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available, image_url
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_all_regardless_of_availability():
        rows = app.db.execute('''
            SELECT id, name, price, available, image_url
            FROM Products
            ''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_product_by_name(product_name):
        rows = app.db.execute('''
SELECT id, name, price, available, image_url
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
            SELECT I.pid AS pid, U.firstname AS firstname, U.lastname AS lastname, I.quantity AS quantity, U.id AS sid
            FROM Inventory I, Products P, Users U
            WHERE I.pid = P.id AND U.id = I.uid AND I.quantity > 0 AND P.name = :product_name
            ''', product_name=product_name)
        return [{'pid': row['pid'], 'firstname': row['firstname'], 'lastname': row['lastname'], 'quantity': row['quantity'], 'sid': row['sid']} for row in rows]

    @staticmethod
    def create_product(name, price, available, image_url):
        try: 
            app.db.execute('''
            INSERT INTO Products(name, price, available, image_url)
            VALUES(:name, :price, :available, :image_url)
            ''', name=name, price=price, available=available, image_url=image_url)
        except SQLAlchemyError:
            return 0
        return result
