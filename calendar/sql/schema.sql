CREATE TABLE IF NOT EXISTS users (
 user_id INTEGER PRIMARY KEY,
 username TEXT NOT NULL,
 pw_hash TEXT NOT NULL,
 email TEXT NULL,
 UNIQUE (username, email)
);

CREATE TABLE IF NOT EXISTS calendars (
 calendar_id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 share_url TEXT NULL,
 UNIQUE (user_id, share_url),
 FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS events (
 event_id INTEGER PRIMARY KEY,
 calendar_id INTEGER NOT NULL,
 title TEXT NOT NULL,
 month INTEGER NOT NULL,
 day INTEGER NOT NULL,
 year INTEGER NULL,
 notes TEXT NULL,
 private INTEGER DEFAULT 0,
 FOREIGN KEY (calendar_id) REFERENCES calendars(calendar_id)
);
