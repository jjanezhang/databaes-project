CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    balance DECIMAL(12,2) NOT NULL CHECK (balance >= 0)
);

CREATE TABLE Sellers (
    sid INT NOT NULL REFERENCES Users(id),
    bid INT NOT NULL REFERENCES Users(id),
    rating INT NOT NULL CHECK(rating BETWEEN 0 AND 5),
    review VARCHAR NOT NULL,
    upvotes INT NOT NUll CHECK (upvotes >= 0),
    time_added timestamp without time zone DEFAULT NULL,
    PRIMARY KEY (sid, bid)
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(1024) NOT NULL,
    created_by INT NOT NULL REFERENCES Users(id)
);

CREATE TABLE Orders (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    time_placed timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE Purchases (
    oid INT NOT NULL REFERENCES Orders(id),
    pid INT NOT NULL REFERENCES Products(id),
    sid INT NOT NULL REFERENCES Users(id),
    fulfilled BOOLEAN NOT NULL,
    time_fulfilled timestamp without time zone DEFAULT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (oid, pid, sid)
);

CREATE TABLE Inventory (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (uid, pid)
);

CREATE TABLE Ratings (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    rating INT NOT NULL CHECK(rating BETWEEN 0 AND 5),
    review VARCHAR NOT NULL,
    upvotes INT NOT NUll CHECK (upvotes >= 0),
    time_added timestamp without time zone DEFAULT NULL,
    PRIMARY KEY (uid, pid)
);

CREATE TABLE Upvotes (
    rid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    cid INT NOT NULL REFERENCES Users(id),
    PRIMARY KEY (rid, pid, cid)
);

CREATE TABLE SellerUpvotes (
    rid INT NOT NULL REFERENCES Users(id),
    sid INT NOT NULL REFERENCES Users(id),
    bid INT NOT NULL REFERENCES Users(id),
    PRIMARY KEY (rid, sid, bid)
);

CREATE TABLE Cart (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    sid INT NOT NULL REFERENCES Users(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY(uid, pid, sid),
    FOREIGN KEY(sid, pid) REFERENCES Inventory(uid, pid) ON DELETE CASCADE
)