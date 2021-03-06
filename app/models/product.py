from unittest import result
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError


class Product:
    def __init__(self, id, name, price, category, description, image_url, created_by):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.image_url = image_url
        self.created_by = created_by

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, name, price, category, description, image_url, created_by
            FROM Products
            WHERE id = :id
            ''', id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
            SELECT id, name, price, category, description, image_url, created_by
            FROM Products
            ''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_product_by_name(product_name):
        rows = app.db.execute('''
            SELECT P.id as id, P.name as name, P.price as price, 
            P.category as category, P.description as description, 
            P.image_url as image_url
            FROM Products P
            WHERE name = :product_name
            ''', product_name=product_name)
        
        # print("Product rows: ", [row for row in rows])
        return rows

    @staticmethod
    def get_pid(product_name):
        rows = app.db.execute('''
            SELECT id
            FROM Products
            WHERE name = :product_name
            ''', product_name=product_name)
        ans = rows[0]['id']
        return int(ans)
        

    @staticmethod
    def get_sellers_and_quantities_for_product(product_name):
        rows = app.db.execute('''
            SELECT I.pid AS pid, U.id AS id, U.firstname AS firstname, U.lastname AS lastname, I.quantity AS quantity
            FROM Inventory I, Products P, Users U
            WHERE I.pid = P.id AND U.id = I.uid AND I.quantity > 0 AND P.name = :product_name
            ''', product_name=product_name)
        return [{'pid': row['pid'], 'seller_id': row['id'], 'firstname': row['firstname'], 'lastname': row['lastname'], 'quantity': row['quantity']} for row in rows]

    @staticmethod
    def create_product(name, price, category, description, image_url, created_by):
        try:
            app.db.execute('''
                INSERT INTO Products(name, price, category, description, image_url, created_by)
                VALUES(:name, :price, :category, :description, :image_url, :created_by)
                ''', name=name, price=price, category=category, description=description, image_url=image_url, created_by=created_by)
        except SQLAlchemyError:
            return 0
        return result

    @staticmethod
    def get_all_products_from_user(uid):
        rows = app.db.execute('''
            SELECT id, name, price, category, description, image_url, created_by
            FROM Products
            WHERE created_by = :uid
            ORDER BY id
        ''', uid=uid)

        return [Product(*row) for row in rows]

    @staticmethod
    def update_product(pid, name, price, category, description, image_url):
        try:
            result = app.db.execute('''
                UPDATE Products
                SET name = :name, price = :price, category = :category,
                description = :description, image_url = :image_url
                WHERE id = :pid
            ''', pid=pid, name=name, price=price, description=description, image_url=image_url, category=category)
        except SQLAlchemyError as e:
            return f"Error: {e}, product name already taken."
        return result
