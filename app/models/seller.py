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
    def get_all_reviews_by_sid(sid):
        rows = app.db.execute('''
            SELECT S.bid as bid
            FROM Sellers S
            WHERE S.sid = :sid
        ''', sid=sid)
        return rows

    @staticmethod
    def get_reviewers_by_bid(bid):
        rows = app.db.execute('''
            SELECT U.firstname as firstname, U.lastname as lastname, 
            S.rating as rating, S.review as review, S.bid as bid, 
            S.upvotes as upvotes
            FROM Sellers S, Users U
            WHERE S.bid = :bid AND S.bid = U.id
        ''', bid=bid)
        return rows if rows else None

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