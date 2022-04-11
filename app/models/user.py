from audioop import add
from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = 0 if not balance else balance

        inventory_rows = app.db.execute('''
            SELECT I.uid AS uid, I.pid AS pid, P.name AS name, I.quantity AS quantity
            FROM Inventory I, Products P
            WHERE I.pid = P.id AND I.uid = :uid
        ''', uid=id)

        self.is_seller = len(inventory_rows) > 0

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
            SELECT password, id, email, firstname, lastname, balance
            FROM Users
            WHERE email = :email
            """,
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
            SELECT email
            FROM Users
            WHERE email = :email
            """,
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(email, password, firstname, lastname, balance, rating)
                VALUES(:email, :password, :firstname, :lastname, :balance, :rating)
                RETURNING id
                """,
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname, 
                                  balance=0, rating=0)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def get_names(id):
        rows = app.db.execute("""
            SELECT firstname, lastname
            FROM Users
            WHERE id = :id
            """, id=id)
        return rows if rows else None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
            SELECT id, email, firstname, lastname, balance
            FROM Users
            WHERE id = :id
            """, id=id)
        return User(*(rows[0])) if rows else None        

    def update_balance(self, withdraw_amt, add_amt):
        try:
            add_amt = 0 if not add_amt else add_amt
            withdraw_amt = 0 if not withdraw_amt else withdraw_amt
            new_balance = app.db.execute(f"""
UPDATE Users SET balance = {float(self.balance) + add_amt - withdraw_amt} 
WHERE id = {self.id}
RETURNING balance
""")        
            self.balance = float(new_balance[0][0])
            return new_balance

        except Exception as e:
            print(str(e))
            return None

