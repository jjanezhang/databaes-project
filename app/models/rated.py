from flask import current_app as app
import sys

class Rated:   # a rated item
    def __init__(self, uid, pid, name, rating):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.rating = rating
    @staticmethod
    # Get all rated items purchased by this user
    def get_all(uid):
        rows = app.db.execute('''
            SELECT R.uid AS uid, R.pid AS pid, P.name AS name, R.rating AS rating
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid
        ''', uid=uid)
        return [Rated(*row) for row in rows]
    
    @staticmethod
    # Add a new rating to a product this user purchased 
    def add_rating(uid, pid, rating):
        result = app.db.execute('''
            INSERT INTO Ratings(uid, pid, rating, review)
            VALUES(:uid, :pid, :rating, :review)
        ''', uid=uid, pid=pid, rating=rating, review="")
        return result

    @staticmethod
    # Update the rating of an item previously rated
    def update_rating(uid, pid, rating):
        result = app.db.execute('''
            UPDATE Ratings SET rating = :rating
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid, rating=rating)
        return result

    @staticmethod
    # Remove a rating from a user's existing ratings
    def remove_rating(uid, pid):
        # TODO: Update item's availability based on quantity
        result = app.db.execute('''
            DELETE FROM Ratings
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)
        return result