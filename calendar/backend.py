import sqlite3
from typing import List, Tuple
from passlib.hash import pbkdf2_sha256 as pbkdf2

# Custom imports
from .classes import User, Calendar, Event

# TODO: Fix update_user to match logic of update_event

class Database:
    '''Object to represent SQLite database connection.'''
    def __init__(self, db_name: str):
        self.name = db_name
        self.connection: sqlite3.Connection
        self.cursor: sqlite3.Cursor

        # Initialize connection and cursor
        try:
            self.connection = self._get_connection()
            self.cursor = self._get_cursor()
        except ConnectionError:
            raise ConnectionError()

    # "Private" methods
    def _get_connection(self) -> sqlite3.Connection:
        ''' Returns a Connection object to a SQLite database. '''
        return sqlite3.connect(self.name)

    def _get_cursor(self) -> sqlite3.Cursor:
        ''' Returns a Cursor object from the Connection object. '''
        return self.connection.cursor()

    def _get_result(self):
        ''' Return first cursor result. '''
        if self.connection and self.cursor:
            return self.cursor.fetchone()

    def _get_all_results(self):
        ''' Return all cursor results. '''
        if self.connection and self.cursor:
            return self.cursor.fetchall()

    def _get_lastrowid(self):
        return self.cursor.lastrowid

    def _execute(self, sql_template, sql_tuple) -> None:
        ''' Shortcut for self.cursor.execute() and self.cursor.commit() '''
        if self.connection and self.cursor:
            self.cursor.execute(sql_template, sql_tuple)
            self.connection.commit()

    def _executemany(self, sql_template, sql_tuple_list) -> None:
        ''' Shortcut for self.cursor.executemany() and self.cursor.commit() '''
        if self.connection and self.cursor:
            self.cursor.executemany(sql_template, sql_tuple_list)
            self.connection.commit()

    def _close_all(self) -> None:
        ''' Close Cursor and Connection objects. '''
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    # Select methods
    def verify_password(self, password, pw_hash) -> bool:
        ''' Verifies password matches the password hash. '''
        return pbkdf2.verify(password, pw_hash)

    def get_user(self, username: str) -> User:
        '''Returns a User object for a given username. '''
        username: Tuple = (username,)
        self._execute("SELECT * FROM users WHERE username = ?", username)
        return User(*self._get_result())

    def get_user_by_id(self, user_id: int) -> User:
        '''Returns a User object for a given user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM users WHERE user_id = ?", uid)
        return User(*self._get_result())

    def get_calendar(self, calendar_id: int) -> Calendar:
        ''' Returns a Calendar object for a given calendar_id. '''
        cid: Tuple = (calendar_id,)
        self._execute("SELECT * FROM calendars WHERE calendar_id = ?", cid)
        return Calendar(*self._get_result())

    def get_calendar_by_user_id(self, user_id: int) -> Calendar:
        ''' Returns a Calendar object for a given user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM calendars WHERE user_id = ?", uid)
        return Calendar(*self._get_result())

    def get_calendar_by_share_url(self, share_url: str) -> Calendar:
        ''' Returns a Calendar object for a given user_id. '''
        s_url: Tuple = (str(share_url))
        self._execute("SELECT * FROM calendars WHERE share_url = ?", s_url)
        return Calendar(*self._get_result())

    def get_all_events(self, calendar_id: int, strip_private=False) -> List[Event]:
        ''' Return list of Event objects that match the provided calendar_id. 
            If strip_private is True, all non-private events will be returned. '''
        cid: Tuple = (calendar_id,)

        if strip_private:
            self._execute("SELECT * FROM events WHERE calendar_id = ? AND private = 0", cid)
        else:
            self._execute("SELECT * FROM events WHERE calendar_id = ?", cid)

        results = self._get_all_results()
        return [Event(*event) for event in results] # list comps are so comfy unf

    def get_event(self, event_id: int) -> Event:
        ''' Return a single event, selected by event_id. '''
        eid: Tuple = (event_id,)
        self._execute("SELECT * FROM events WHERE event_id = ?", eid)
        return Event(*self._get_result())

    # Insert methods
    def insert_user(self, username, password, email=None):
        ''' Inserts a new User into the users table. Returns the user_id of the new User. '''
        new_user_template = "INSERT INTO users (username, pw_hash, email) \
                             VALUES (?,?,?)"
        password_hash = pbkdf2.hash(str(password))
        new_user: Tuple = (username, password_hash, email)

        self._execute(new_user_template, new_user)
        return self._get_lastrowid()

    def insert_calendar(self, user_id):
        ''' Inserts a new Calendar into the calendars table. 
            Returns the calendar_id of the new calendar. ''' 
        new_calendar_template = "INSERT INTO calendars (user_id) VALUES (?)"
        new_calendar: Tuple = (user_id,)

        self._execute(new_calendar_template, new_calendar)
        return self._get_lastrowid()

    def insert_event(self, calendar_id, title, month, day,
                     year=None, notes=None, private=None):
        ''' Inserts a new Event into the events table. Returns event_id of the new Event. '''
        new_event_template = "INSERT INTO events \
                              (calendar_id, title, month, day, year, notes, private) \
                              VALUES (?,?,?,?,?,?,?)"
        new_event: Tuple = (calendar_id, title, month, day, year, notes, private)

        self._execute(new_event_template, new_event)
        return self._get_lastrowid()

    # Update methods
    def update_user(self, user: User, username=None, pw_hash=None, email=None) -> None:
        ''' Update user attributes in the database. '''
        u, uid = user, user.id
        updates: List[Tuple] = []
        delta = lambda x, y: x != y
        add_update = lambda item, value: updates.append((item, value, uid))
        # maybe refactor the lambdas into their own function

        if delta(u.username, username):
            add_update('username', username)
        if delta(u.pw_hash, pw_hash):
            add_update('pw_hash', pw_hash)
        if delta(u.email, email):
            add_update('email', email)

        self._executemany("UPDATE users SET ? = ? WHERE user_id = ?", updates)

    def update_calendar_share_url(self, calendar: Calendar):
        ''' Updates share_url value of a Calendar. '''
        c_tuple = (calendar.share_url, calendar.id)
        self._execute("UPDATE calendars SET share_url = ? WHERE calendar_id = ?", c_tuple)

    def update_event(self, event: Event) -> None:
        ''' Takes an event and any event field updates, and updates the event
            in the database.'''

        # Get event as how it's stored in the database, and make comparisons to the current
        # values of event. Collect changes and update event
        db_event = self.get_event(event.id)

        delta = lambda x, y: x != y
        gen_tuple = lambda x: (x, event.id)
        gen_template = lambda x: "UPDATE events SET {} = ? WHERE event_id = ?".format(x)

        # God this is a mess
        if delta(db_event.title, event.title):
            self._execute(gen_template('title'), gen_tuple(event.title))

        if delta(db_event.month, event.month):
            self._execute(gen_template('month'), gen_tuple(event.month))

        if delta(db_event.day, event.day):
            self._execute(gen_template('day'), gen_tuple(event.day))

        if delta(db_event.year, event.year):   # There's probably a better way to do this
            self._execute(gen_template('year'), gen_tuple(event.year))

        if delta(db_event.notes, event.notes):
            self._execute(gen_template('notes'), gen_tuple(event.notes))

        if delta(db_event.private, event.private):
            self._execute(gen_template('private'), gen_tuple(event.private))

    # Delete methods
    def delete_user(self, user: User) -> None:
        ''' Deletes a User from the database. '''
        uid = (user.id,)
        self._execute("DELETE FROM users WHERE user_id = ? LIMIT 1", uid)

    def delete_calendar(self, calendar: Calendar) -> None:
        ''' Deletes a Calendar from the database. '''
        cid = (calendar.id,)
        self._execute("DELETE FROM calendars WHERE calendar_id = ? LIMIT 1", cid)

    def delete_event(self, event: Event) -> None:
        ''' Deletes an Event from the database. '''
        eid = (event.id,)
        self._execute("DELETE FROM events WHERE event_id = ? LIMIT 1", eid)

    def delete_calendar_events(self, calendar: Calendar) -> None:
        ''' Deletes all of a Calendar's Events from the database. '''
        cid = (calendar.id,)
        self._execute("DELETE FROM events WHERE calendar_id = ?", cid)
