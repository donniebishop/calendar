INSERT INTO users
 (username, pw_hash) 
VALUES
 ('bushidoboy', 'abcdefg'),
 ('covabishop', 'efgabcd'),
 ('afran646', 'bcdefga');

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