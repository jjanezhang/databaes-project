from flask import current_app as app
import sys

class Seller:   # a rated item
    def __init__(self, uid, bid, rating, review, time_added):
        self.uid = uid
        self.bid = bid
        self.rating = rating
        self.review = review
        self.time_added = time_added    
    
    
    @staticmethod
    # Get all rated items purchased by this user
    def avg_rating_for_seller(sid):
        rows = app.db.execute('''
            SELECT ROUND(AVG(S.rating),1) AS rating
            FROM Sellers S
            WHERE S.sid = :sid
        ''', sid=sid)
        rowcount = len(rows)
        if rowcount>0:
            return rows
        return []    
 
    @staticmethod
    # Was this seller already rated by this buyer? sid=seller_id, bid=buyer_id
    def already_rated(sid, bid):
        rows = app.db.execute('''
            SELECT S.rating AS rating
            FROM Sellers S
            WHERE S.sid = :sid AND S.bid = :bid
        ''', sid=sid, bid=bid)
        rowcount = len(rows)
        if rowcount>0:
            return True
        return False

    @staticmethod
    # Was this seller already rated by this buyer? sid=seller_id, bid=buyer_id
    def add_rating(sid, bid, rating, review="", upvotes=0):
        result = app.db.execute('''
            INSERT INTO Sellers(sid, bid, rating, review, upvotes, time_added)
            VALUES(:sid, :bid, :rating, :review, :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (sid, bid) DO NOTHING;
        ''', sid=sid, bid=bid, rating=rating, review=review, upvotes=upvotes)
        return result

    @staticmethod
    def num_ratings_for_seller(sid):
        rows = app.db.execute('''
            SELECT COUNT(*) as num_ratings
            FROM Sellers S
            WHERE S.sid = :sid
        ''', sid=sid)
        rowcount = len(rows)
        if rowcount>0:
            return rows
        return 0