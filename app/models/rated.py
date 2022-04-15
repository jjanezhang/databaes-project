from flask import current_app as app


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
<<<<<<< HEAD
            R.rating as rating, R.review as review
=======
            R.rating as rating, R.review AS review
>>>>>>> main
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid
            ORDER BY time_added DESC
        ''', uid=uid)
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
    # TODO: Actually need all people who purchased this product
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
        return len(rows) > 0

    @staticmethod
    # Already reviewed this product by this uid?
    def already_reviewed(uid, pid):
        rows = app.db.execute('''
            SELECT R.review as review
            FROM Ratings R, Products P
            WHERE R.pid = P.id AND R.uid = :uid AND R.pid = :pid
        ''', uid=uid, pid=pid)
        result = [row['review'] for row in rows]
        # print("ROWSS for already reviewed: ", result)
        if result == []:
            return False
        return True

    @staticmethod
    def ratings_for_all_products():
        rows = app.db.execute('''
            SELECT id, ROUND(AVG(rating),1) AS average_rating, count(rating) AS num_ratings
            FROM Products LEFT JOIN Ratings ON id = pid
            GROUP BY id
        ''')
        return [{'avg_rating': row['average_rating'] if row['average_rating'] else 0, 
                'num_ratings': row['num_ratings'] if row['num_ratings'] else 0} for row in rows]

    @staticmethod
    # Get all rated items purchased by this user
    def avg_rating_for_product(pid):
        rows = app.db.execute('''
            SELECT ROUND(AVG(R.rating),1) AS rating
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)

        if rows[0]['rating']==None:
            return 0
        return float(rows[0]['rating'])

    @staticmethod
    def num_ratings_for_product(pid):
        rows = app.db.execute('''
            SELECT COUNT(*) as num_ratings
            FROM Ratings R
            WHERE R.pid = :pid
        ''', pid=pid)

        # print("num ratings is: ",rows[0]['num_ratings'] )
        if rows[0]['num_ratings']==None:
            return 0
        return int(rows[0]['num_ratings'])


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
        ''', uid=uid, pid=pid, rating=0, review="", upvotes=0, new_upvotes=current_upvotes+1)
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

    @staticmethod
    def already_upvoted(reviewer_id, pid, upvoter_id):
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
