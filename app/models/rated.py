from flask import current_app as app
import sys

class Rated:   # a rated item
    def __init__(self, uid, pid, name):
        self.uid = uid
        self.pid = pid
        self.name = name

    @staticmethod
    # Get all rated items purchased by this user
    def get_all_by_uid(uid):
        rows = app.db.execute('''
            SELECT R.uid as uid, R.pid AS pid, P.name AS name,
            R.rating as rating
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid
            ORDER BY time_added DESC
        ''', uid=uid)
        for row in rows:
            print("row: ", row)
        # return [Rated(*row) for row in rows]
        return rows
    
    @staticmethod
    def get_all_reviews_by_pid(pid):
        rows = app.db.execute('''
            SELECT R.review as review, R.uid as uid, R.rating as rating
            FROM Ratings R
            WHERE R.pid = :pid
            ORDER BY R.time_added DESC
        ''', pid=pid)
        return rows
    
    @staticmethod
    def get_reviews_and_reviewers_by_pid_uid(pid, uid):
        rows = app.db.execute('''
            SELECT U.firstname as firstname, U.lastname as lastname, 
            R.rating as rating, R.review as review, R.upvotes as upvotes,
            R.time_added as time_added
            FROM Ratings R, Users U
            WHERE R.pid = :pid AND R.uid = U.id AND U.id = :uid
            ORDER BY R.time_added DESC
        ''', pid=pid, uid=uid)
        return rows if rows else None
    
    @staticmethod
    # Already rated this product by this uid?
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
    # Already reviewed this product by this uid?
    def already_reviewed(uid, pid):
        rows = app.db.execute('''
            SELECT R.review as review
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid AND R.pid = :pid
        ''', uid=uid, pid=pid)
        rowcount = len(rows)
        result = [row['review'] for row in rows]
        # print("ROWSS for already reviewed: ", result)
        # if rowcount>0:
        if result[0]=="":
            return False
        return True
    
    @staticmethod
    # Get all rated items purchased by this user
    def avg_rating_for_product(pid):
        rows = app.db.execute('''
            SELECT ROUND(AVG(R.rating),1) AS rating
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)
        rowcount = len(rows)
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
    # how many upvotes for this review?
    def num_upvotes(uid, pid):
        result = app.db.execute('''
            SELECT R.upvotes as num_upvotes
            FROM Ratings R
            WHERE R.uid = :uid AND R.pid = :pid
        ''', uid=uid, pid=pid)
        return [r for r in result][0]

    @staticmethod
    # Add a new rating to a product this user purchased 
    def add_rating(uid, pid, rating, review=""):
        result = app.db.execute('''
            INSERT INTO Ratings(uid, pid, rating, review, upvotes, time_added)
            VALUES(:uid, :pid, :rating, :review, :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (uid, pid) DO NOTHING;
        ''', uid=uid, pid=pid, rating=rating, review=review, upvotes=0)
        return result

    @staticmethod
    # Add a new rating to a product this user purchased 
    def add_review(uid, pid, review):
        result = app.db.execute('''
            INSERT INTO Ratings(uid, pid, rating, review, upvotes, time_added)
            VALUES(:uid, :pid, :rating, :review, :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (uid, pid) DO UPDATE
            SET rating = Ratings.rating, review=EXCLUDED.review;
        ''', uid=uid, pid=pid, rating=0, review=review, upvotes=0)
        return result

    @staticmethod
    # Add an upvote to a review 
    def add_upvote(uid, pid, current_upvotes):
        result = app.db.execute('''
            INSERT INTO Ratings(uid, pid, rating, review, 
            upvotes, time_added)
            VALUES(:uid, :pid, :rating, :review, 
            :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (uid, pid) DO UPDATE
            SET upvotes = :new_upvotes;
        ''', uid=uid, pid=pid, rating=0, review="", 
        upvotes=0, new_upvotes=current_upvotes+1)
        return result
    
    @staticmethod
    # Record this upvote
    def record_upvote(upvote_receiver_uid, pid, current_user_id):
        result = app.db.execute('''
            INSERT INTO Upvotes(rid, pid, cid)
            VALUES(:rid, :pid, :cid)
            ON CONFLICT (rid, pid, cid) DO NOTHING;
        ''', rid=upvote_receiver_uid, pid=pid, cid=current_user_id)
        return result

    @staticmethod
    # Add an upvote to a review 
    def get_current_upvotes(uid, pid):
        result = app.db.execute('''
            SELECT R.upvotes as current_upvotes
            FROM Ratings R
            WHERE R.uid = :uid AND R.pid = :pid
        ''', uid=uid, pid=pid)
        return [r for r in result][0]

    # @staticmethod
    # # Add an upvote to a review 
    # def already_upvoted(uid, pid, current_user_id):
    #     result = app.db.execute('''
    #         SELECT R.last_upvoted_by as last_upvoted_by
    #         FROM Ratings R
    #         WHERE R.uid = :uid AND R.pid = :pid
    #     ''', uid=uid, pid=pid)

    #     last_upvoter = [r for r in result][0]['last_upvoted_by']
    #     if last_upvoter == current_user_id:
    #         return True
    #     return False

    @staticmethod
    # Check 
    def already_upvoted(reviewer_id, pid, upvoter_id): # upvoter = current user =cid
        result = app.db.execute('''
            SELECT U.rid
            FROM Upvotes U
            WHERE U.rid = :rid AND U.pid = :pid AND U.cid = :cid
        ''', rid=reviewer_id, pid=pid, cid=upvoter_id)

        # print("result: ", result)
        return result !=[]

    @staticmethod
    # Update the rating of an item previously rated
    def update_rating(uid, pid, rating):
        result = app.db.execute('''
            UPDATE Ratings SET rating = :rating
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid, rating=rating)
        return result

    @staticmethod
    # Update the review of an item previously rated
    def update_review(uid, pid, review):
        result = app.db.execute('''
            UPDATE Ratings SET review = :review
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid, review=review)
        return result

    @staticmethod
    # Remove a rating (including review) from a user's existing ratings
    def remove_rating(uid, pid):
        result = app.db.execute('''
            DELETE FROM Ratings
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)
        return result
    
    @staticmethod
    # Remove a review - but not the rating - from a user's existing ratings
    def remove_review(uid, pid):
        result = app.db.execute('''
            UPDATE Ratings SET review = :review
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid, review="")
        return result
    