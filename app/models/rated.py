from flask import current_app as app
import sys

class Rated:   # a rated item
    def __init__(self, uid, pid, name, rating, review, time_added):
        self.uid = uid
        self.pid = pid
        self.name = name
        self.rating = rating
        self.review = review
        self.time_added = time_added

    @staticmethod
    # Get all rated items purchased by this user
    def get_all_by_uid(uid):
        rows = app.db.execute('''
            SELECT R.uid as uid, R.pid AS pid, P.name AS name, 
            R.rating AS rating, R.review as review, R.time_added as time_added
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid
            ORDER BY time_added DESC
        ''', uid=uid)
        for row in rows:
            print("row: ", row)
        return [Rated(*row) for row in rows]
    
    @staticmethod
    def get_all_reviews_by_pid(pid):
        rows = app.db.execute('''
            SELECT R.review as review, R.uid as uid, R.rating as rating
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)
        return rows
    
    @staticmethod
    def get_reviews_and_reviewers_by_pid_uid(pid, uid):
        rows = app.db.execute('''
            SELECT U.firstname as firstname, U.lastname as lastname, 
            R.rating as rating, R.review as review, R.uid as uid
            FROM Ratings R, Users U
            WHERE R.pid = :pid AND R.uid = U.id AND U.id = :uid
        ''', pid=pid, uid=uid)
        return rows if rows else None
    
    @staticmethod
    # Get all rated items purchased by this user
    def already_rated(uid, pid):
        rows = app.db.execute('''
            SELECT R.uid AS uid, R.pid AS pid, P.name AS name, R.rating AS rating
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid AND R.pid = :pid
        ''', uid=uid, pid=pid)
        rowcount = len(rows)
        if rowcount>0:
            return True
        return False
    
    @staticmethod
    # Get all rated items purchased by this user
    def avg_rating_for_product(pid):
        rows = app.db.execute('''
            SELECT ROUND(AVG(R.rating),1) AS rating
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)
        rowcount = len(rows)
        # print("rows: ", rows)
        if rowcount>0:
            return rows
        return []
        
    @staticmethod
    def num_ratings_for_product(pid):
        rows = app.db.execute('''
            SELECT COUNT(*) as num_ratings
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)
        rowcount = len(rows)
        if rowcount>0:
            return rows
        return 0

    @staticmethod
    # Add a new rating to a product this user purchased 
    def add_rating(uid, pid, rating, review=""):
        result = app.db.execute('''
            INSERT INTO Ratings(uid, pid, rating, review)
            VALUES(:uid, :pid, :rating, :review)
            ON CONFLICT (uid, pid) DO NOTHING;
        ''', uid=uid, pid=pid, rating=rating, review=review)
        return result

    @staticmethod
    # Update the rating of an item previously rated
    def update_rating(uid, pid, rating, review=""):
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
    
    @staticmethod
    # how many upvotes for this review?
    def num_upvotes(uid):
        # TODO: Update item's availability based on quantity
        result = app.db.execute('''
            SELECT R.upvotes as num_upvotes
            FROM Ratings R
            WHERE R.uid = :uid
        ''', uid=uid)
        return result