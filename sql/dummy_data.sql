INSERT INTO users
 (username, pw_hash, calendar_id) 
VALUES
 ('bushidoboy', 'abcdefg', 1),
 ('covabishop', 'efgabcd', 2),
 ('afran646', 'bcdefga', 3);

INSERT INTO events
 (calendar_id, title, month, day, year)
VALUES
 (2, 'Someday', 6, 12, 2010),
 (3, 'Birthday', 3, 28, 1996),
 (1, 'Website', 3, 29, 2018);

INSERT INTO calendars
 (user_id)
VALUES
 (1),
 (2),
 (3);