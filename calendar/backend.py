import sqlite3
from typing import List, Tuple
from passlib.hash import pbkdf2_sha256 as pbkdf2

# Custom imports
from .classes import User, Calendar, Event

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
        user = self._get_result()

        return User(*user)

    def get_user_by_id(self, user_id: int) -> User:
        '''Returns a User object for a given user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM users WHERE user_id = ?", uid)
        user = self._get_result()

        return User(*user)

    def get_calendar(self, calendar_id: int) -> Calendar:
        ''' Returns a Calendar object for a given calendar_id. '''
        cid: Tuple = (calendar_id,)
        self._execute("SELECT * FROM calendars WHERE calendar_id = ?", cid)
        calendar = self._get_result()

        return Calendar(*calendar)

    def get_calendar_by_user_id(self, user_id: int) -> Calendar:
        ''' Returns a Calendar object for a given user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM calendars WHERE user_id = ?", uid)
        return Calendar(*self._get_result())

    def get_all_events(self, calendar_id: int) -> List[Event]:
        ''' Return list of Event objects that match the provided calendar_id. '''
        cid: Tuple = (calendar_id,)
        self._execute("SELECT * FROM events WHERE calendar_id = ?", cid)
        results = self._get_all_results()

        return [Event(*event) for event in results]

    def get_event(self, event_id: int) -> Event:
        ''' Return a single event, selected by event_id. '''
        eid: Tuple = (event_id,)
        self._execute("SELECT * FROM events WHERE event_id = ?", eid)
        event = self._get_result()

        return Event(*event)

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
    #def update_user(self):
        #''' Update user attributesa in the database. '''

    def update_event(self, event: Event, title=None, month=None,
                     day=None, year=None, notes=None, private=0) -> None:
        ''' Takes an event and any event field updates, and updates the event
            in the database.'''
        e = event
        eid = event.id
        updates: List[Tuple] = []
        delta = lambda x, y: x != y
        add_update = lambda item, value: updates.append((item, value, eid))

        # For any field that has a non-default value, add_update adds a tuple
        # of the field and the new value, as well as the event_id. Only added
        # if the original value has changed

        # There's probably a better way to iterate through these
        if delta(e.title, title):
            add_update('title', title)
        if delta(e.month, month):
            add_update('month', month)
        if delta(e.day, day):
            add_update('day', day)
        if delta(e.year, year):
            add_update('year', year)
        if delta(e.notes, notes):
            add_update('notes', notes)
        if delta(e.private, private):
            add_update('private', private)

        # Cursor.executemany() takes a template and a list of tuples which it
        # unpacks to execute against the DB. Set values are taken from the fields
        # and values that add_update was called against, and they all have the
        # event_id in their tuple so that the same event gets updated as much
        # as it needs.
        #
        # I could have written just a bunch of functions to do this.
        # But I didn't.
        update_event_template = "UPDATE events SET ? = ? WHERE event_id = ?"
        self._executemany(update_event_template, updates)

    # Delete methods
    def delete_user(self, user_id):
        ''' Deletes a User from the database. '''
        pass