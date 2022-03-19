from flask import current_app as app


class Purchase:
    def __init__(self, oid, pid, sid, fulfilled, time_fulfilled, price):
        self.oid = oid
        self.pid = pid
        self.sid = sid
        self.fulfilled = fulfilled
        self.time_fulfilled = time_fulfilled
        self.price = price

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
            SELECT P.oid AS oid, P.pid AS pid, P.sid AS sid, P.fulfilled AS fulfilled,
            P.time_fulfilled AS time_fulfilled, P.price AS price
            FROM Purchases P, Orders O
            WHERE O.id = P.oid AND O.uid = :uid
            AND O.time_placed >= :since
            ORDER BY O.time_placed DESC
            '''
        , uid=uid, since=since)
        return [Purchase(*row) for row in rows]
