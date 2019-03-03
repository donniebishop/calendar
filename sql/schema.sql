CREATE TABLE calendars (
 calendar_id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 share_url TEXT NULL
);

CREATE UNIQUE INDEX userID
ON calendars (userID);

CREATE TABLE users (
 user_id INTEGER PRIMARY KEY,
 username TEXT NOT NULL,
 email TEXT NULL,
 pw_hash TEXT NOT NULL,
 calendar_id INTEGER NOT NULL
);

CREATE TABLE events (
 event_id INTEGER PRIMARY KEY,
 calendar_id INTEGER NOT NULL,
 title TEXT NOT NULL,
 month INTEGER NOT NULL,
 day INTEGER NOT NULL,
 year INTEGER NULL,
 notes TEXT NULL
);

