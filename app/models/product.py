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

    # @staticmethod
    # def get_all_regardless_of_availability_by_uid(uid):
    #     rows = app.db.execute('''
    #         SELECT id, uid, name, price, available
    #         FROM Products
    #         WHERE uid = :uid
    #         ''')
    #     return [Product(*row) for row in rows]
        #return [[Product(*row).uid, Product(*row).name] for row in rows]
