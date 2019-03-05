CREATE TABLE calendars (
 calendar_id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 share_url TEXT NULL
);

CREATE UNIQUE INDEX user_id
ON calendars (user_id);

CREATE TABLE users (
 user_id INTEGER PRIMARY KEY,
 username TEXT NOT NULL,
 pw_hash TEXT NOT NULL,
 email TEXT NULL
);

CREATE TABLE events (
 event_id INTEGER PRIMARY KEY,
 calendar_id INTEGER NOT NULL,
 title TEXT NOT NULL,
 month INTEGER NOT NULL,
 day INTEGER NOT NULL,
 year INTEGER NULL,
 notes TEXT NULL,
 private INTEGER DEFAULT 0
);
