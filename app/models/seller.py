from flask import current_app as app

class Seller:   # a rated item
    def __init__(self, uid, bid, rating, review, time_added):
        self.uid = uid
        self.bid = bid
        self.rating = rating
        self.review = review
        self.time_added = time_added

    # @staticmethod
    # def get_all_by_bid(bid):
    #     # uid is buyer, match on U.id to get names,
    #     rows = app.db.execute('''
    #         SELECT P.sid as sid, 
    #         CONCAT(U.firstname, ' ', U.lastname) AS name,
    #         S.rating as rating, S.review as review
    #         FROM Sellers S, Purchases P, Users U, Orders O
    #         WHERE O.uid = :bid AND O.id=P.oid AND P.sid = S.sid AND U.id = S.sid
    #         ORDER BY time_added DESC
    #     ''', bid=bid)
    #     return rows
    
    @staticmethod
    def get_all_by_bid(bid):
        # uid is buyer, match on U.id to get names,
        rows = app.db.execute('''
            SELECT S.sid as sid, 
            CONCAT(U.firstname, ' ', U.lastname) AS name,
            S.rating as rating, S.review as review
            FROM Sellers S, Users U
            WHERE S.bid = :bid AND U.id=S.sid
            ORDER BY time_added DESC
        ''', bid=bid)
        return rows

    @staticmethod
    def get_all_reviews_for_sid(sid):
        # TODO: check if ordering by time_added actually saves us the second sort
        rows = app.db.execute('''
            SELECT S.bid as bid, S.review as review, S.rating as rating,
            S.upvotes as upvotes, S.time_added as time_added,
            U.firstname as firstname, U.lastname as lastname
            FROM Sellers S, Users U
            WHERE S.bid = U.id AND S.sid = :sid
            ORDER BY S.time_added DESC
        ''', sid=sid)
        return rows

    @staticmethod
    def check_bought_by_sid_bid(sid, bid):
        rows = app.db.execute('''
            SELECT P.sid as sid
            FROM Purchases P, Orders O
            WHERE P.oid = O.id AND P.sid = :sid AND O.uid = :bid
        ''', sid=sid, bid=bid)
        result = [row['sid'] for row in rows]
        # print("Bought from this seller result: ", result)
        if result == []:
            return False
        return True

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

        print("avg seller rating is: ", rows[0]['rating'])
        if rows[0]['rating']==None:
            return 0
        return float(rows[0]['rating'])
    
    @staticmethod
    def num_ratings_for_seller(sid):
        rows = app.db.execute('''
            SELECT COUNT(*) as num_ratings
            FROM Sellers S
            WHERE S.sid = :sid
        ''', sid=sid)
        # print("number of ratings for seller is: ", rows[0]['num_ratings'])
        if rows[0]['num_ratings']==None:
            return 0
        return int(rows[0]['num_ratings'])

    @staticmethod
    def get_current_review(sid, bid):
        rows = app.db.execute('''
            SELECT S.review as review
            FROM Sellers S
            WHERE S.bid = :bid AND S.sid = :sid
        ''', sid=sid, bid=bid)

        # print("review is: ", rows[0]['review'])
        return rows[0]['review']
    
    @staticmethod
    # Already reviewed this seller by this uid?
    def already_reviewed(sid, bid):
        rows = app.db.execute('''
            SELECT S.review as review
            FROM Sellers S
            WHERE S.bid = :bid AND S.sid = :sid
        ''', sid=sid, bid=bid)
        result = [row['review'] for row in rows]

        print("checking if already reviewed. Matches(bid) are: ... ", result)
        if result == [""] or result ==[]:
            return False
        return True
    
    # @staticmethod
    # # Already reviewed this seller by this uid?
    # def already_reviewed(sid, bid):
    #     rows = app.db.execute('''
    #         SELECT S.review as review
    #         FROM Sellers S
    #         WHERE S.bid = :bid AND S.sid = :sid
    #     ''', sid=sid, bid=bid)
    #     result = [row['review'] for row in rows]

    #     print("checking if already reviewed. Matches(bid) are: ... ", result)
    #     if result == [""] or result ==[]:
    #         return False
    #     return True

    @staticmethod
    def already_rated(sid, bid):
        rows = app.db.execute('''
            SELECT S.rating AS rating
            FROM Sellers S
            WHERE S.sid = :sid AND S.bid = :bid
        ''', sid=sid, bid=bid)
        # print("is this already rated? ", len(rows))
        if len(rows) > 0:
            return True
        return False
    
    @staticmethod
    def already_upvoted_seller(reviewer_id, seller_id, buyer_id): # who is upvoting (current user) + which seller is being reviewed + which buyer's review it is that is being upvoted
        result = app.db.execute('''
            SELECT SU.rid
            FROM SellerUpvotes SU
            WHERE SU.rid = :rid AND SU.sid = :sid AND SU.bid = :bid
        ''', rid=reviewer_id, sid=seller_id, bid=buyer_id)

        # print("result: ", result)
        return result !=[]

    @staticmethod
    def get_current_upvotes(sid, bid): # number of upvotes to review of buyer (bid) given to seller (sid)
        result = app.db.execute('''
            SELECT S.upvotes as current_upvotes
            FROM Sellers S
            WHERE S.sid = :sid AND S.bid = :bid
        ''', sid=sid, bid=bid)
        return [r for r in result][0]

    @staticmethod
    # Add an upvote to a review
    def add_upvote(sid, bid, current_upvotes):
        result = app.db.execute('''
            INSERT INTO Sellers(sid, bid, rating, review, 
            upvotes, time_added)
            VALUES(:sid, :bid, :rating, :review, 
            :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (sid, bid) DO UPDATE
            SET upvotes = :new_upvotes;
        ''', sid=sid, bid=bid, rating=0, review="", upvotes=current_upvotes, new_upvotes=current_upvotes+1)
        return result

    @staticmethod
    # Record this upvote
    def record_upvote(reviewer_id, seller_id, buyer_id):
        result = app.db.execute('''
            INSERT INTO SellerUpvotes(rid, sid, bid)
            VALUES(:rid, :sid, :bid)
            ON CONFLICT (rid, sid, bid) DO NOTHING;
        ''', rid=reviewer_id, sid=seller_id, bid=buyer_id)
        return result

    @staticmethod
    def add_rating(sid, bid, new_rating):
        result = app.db.execute('''
            INSERT INTO Sellers(sid, bid, rating, review, upvotes, time_added)
            VALUES(:sid, :bid, :rating, :review, :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (sid, bid) DO UPDATE
            SET rating = :new_rating;
        ''', sid=sid, bid=bid, rating=new_rating, new_rating=new_rating, review="", upvotes=0)
        return result

    @staticmethod
    # Add a new review to a product this user purchased
    def add_review(seller_id, buyer_id, review): #
        result = app.db.execute('''
            INSERT INTO Sellers(sid, bid, rating, review, upvotes, time_added)
            VALUES(:sid, :bid, :rating, :review, :upvotes, LOCALTIMESTAMP(1))
            ON CONFLICT (sid, bid) DO UPDATE
            SET rating = Sellers.rating, review=EXCLUDED.review;
        ''', sid=seller_id, bid=buyer_id, rating=0, review=review, upvotes=0)
        return result

    @staticmethod
    def update_rating(bid,sid, rating):
        result = app.db.execute('''
            UPDATE Sellers SET rating = :rating
            WHERE sid = :sid AND bid = :bid
        ''', sid=sid, bid=bid, rating=rating)
        return result
    
    @staticmethod
    def update_review(bid, sid, review):
        result = app.db.execute('''
            UPDATE Sellers SET review = :review
            WHERE bid = :bid AND sid = :sid
        ''', bid=bid, sid=sid, review=review)
        return result
    
    @staticmethod
    def remove_rating(bid, sid):
        result = app.db.execute('''
            DELETE FROM Sellers
            WHERE bid = :bid AND sid = :sid
        ''', bid=bid, sid=sid)
        return result

    @staticmethod
    def remove_review(bid, sid):
        result = app.db.execute('''
            UPDATE Sellers SET review = :review
            WHERE bid = :bid AND sid = :sid
        ''', bid=bid, sid=sid, review="")
        return result