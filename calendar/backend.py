from sqlite3 import connect as connect_db
from sqlite3 import Connection, Cursor
from typing import List, Tuple
from passlib.hash import pbkdf2_sha256 as pbkdf2

# Custom imports
from .classes import User, Calendar, Event

# TODO: Fix update_user to match logic of update_event

class Repository:
    ''' Repository acts as the interface to the database. User methods are available through 
        the self.users Data Access Object (DAO), calendar methods through self.calendars, 
        and event methods through self.events '''
    def __init__(self, database: str):
        self._connection = connect_db(database)
        self.users = UserDAO(self._connection)
        self.calendars = CalendarDAO(self._connection)
        self.events = EventDAO(self._connection)
        self.create_tables()

    def _close(self):
        ''' Commit all changes and close out connection to Database. '''
        self._connection.commit()
        self._connection.close()

    def create_tables(self):
        ''' Creates tables in the database. schema.sql uses IF NOT EXISTS so it only creates tables
            if they don't already exist in the databse. '''
        with open('calendar/sql/schema.sql') as schema:
            create_table_script = ''.join(schema.readlines())
            self._connection.executescript(create_table_script)


class BaseDAO:
    ''' Generic Data Access Object (DAO). Provides wrappers to SQL functions
        and all DAO classes inherit from this '''
    def __init__(self, connection: Connection):
        self._connection = connection
        self._cursor = self._connection.cursor()

    # "Private" methods
    def _get_cursor(self) -> Cursor:
        ''' Returns a Cursor object from the Connection object. '''
        return self._connection.cursor()

    def _get_result(self):
        ''' Return first cursor result. '''
        return self._cursor.fetchone()

    def _get_all_results(self):
        ''' Return all cursor results. '''
        return self._cursor.fetchall()

    def _get_lastrowid(self):
        return self._cursor.lastrowid

    def _execute(self, sql_template, sql_tuple=None) -> None:
        ''' Shortcut for self.cursor.execute() '''
        if sql_tuple:
            self._cursor.execute(sql_template, sql_tuple)
        else:
            self._cursor.execute(sql_template)

    def _executemany(self, sql_template, sql_tuple_list) -> None:
        ''' Shortcut for self.cursor.executemany() '''
        self._cursor.executemany(sql_template, sql_tuple_list)


class UserDAO(BaseDAO):
    ''' Data Access Object for the users table in the database. '''

    def verify_password(self, password, pw_hash) -> bool:
        ''' Verifies password matches the password hash. '''
        return pbkdf2.verify(password, pw_hash)

    def get_user(self, username: str) -> User:
        ''' Returns a User object for a given username. '''
        username: Tuple = (username,)
        self._execute("SELECT * FROM users WHERE username = ?", username)
        return User(*self._get_result())

    def get_user_by_id(self, user_id: int) -> User:
        ''' Returns a User object for a given user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM users WHERE user_id = ?", uid)
        return User(*self._get_result())

    def get_username_by_id(self, user_id: int) -> str:
        ''' Returns the username associated with the user_id. '''
        uid: Tuple = (user_id,)
        self._execute("SELECT * FROM users WHERE user_id = ?", uid)
        user = User(*self._get_result())
        return user.username

    def insert_user(self, username, password, email=None):
        ''' Inserts a new User into the users table. '''
        new_user_template = "INSERT INTO users (username, pw_hash, email) \
                             VALUES (?,?,?)"
        password_hash = pbkdf2.hash(str(password))
        new_user: Tuple = (username, password_hash, email)

        self._execute(new_user_template, new_user)

    def update_user(self, user: User) -> None:
        ''' Update user attributes in the database. '''
        db_user = self.get_user_by_id(user.id)
        updates = []
        delta = lambda x, y: x != y

        def add_update(field, value) -> str:
            update = "UPDATE users SET {} = '{}' where user_id = {}".format(field, value, user.id)
            updates.append(update)

        if delta(db_user.username, user.username):
            add_update('username', user.username)
        if delta(db_user.pw_hash, user.pw_hash):
            add_update('pw_hash', user.pw_hash)
        if delta(db_user.email, user.email):
            add_update('email', user.email)

        for update in updates:
            self._execute(update)

    def delete_user(self, user: User) -> None:
        ''' Deletes a User from the database. '''
        uid = (user.id,)
        self._execute("DELETE FROM users WHERE user_id = ? LIMIT 1", uid)


class CalendarDAO(BaseDAO):
    ''' Data Access Object for calendars table in the database. '''

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

    def insert_calendar(self, user_id):
        ''' Inserts a new Calendar into the calendars table. 
            Returns the calendar_id of the new calendar. ''' 
        new_calendar_template = "INSERT INTO calendars (user_id) VALUES (?)"
        new_calendar: Tuple = (user_id,)

        self._execute(new_calendar_template, new_calendar)
        return self._get_lastrowid()

    def update_calendar_share_url(self, calendar: Calendar):
        ''' Updates share_url value of a Calendar. '''
        c_tuple = (calendar.share_url, calendar.id)
        self._execute("UPDATE calendars SET share_url = ? WHERE calendar_id = ?", c_tuple)

    def delete_calendar(self, calendar: Calendar) -> None:
        ''' Deletes a Calendar from the database. '''
        cid = (calendar.id,)
        self._execute("DELETE FROM calendars WHERE calendar_id = ? LIMIT 1", cid)


class EventDAO(BaseDAO):
    ''' Data Access Object for events table in the database.'''

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

    def insert_event(self, calendar_id, title, month, day,
                     year=None, notes=None, private=None) -> None:
        ''' Inserts a new Event into the events table. Returns event_id of the new Event. '''
        new_event_template = "INSERT INTO events \
                              (calendar_id, title, month, day, year, notes, private) \
                              VALUES (?,?,?,?,?,?,?)"
        new_event: Tuple = (calendar_id, title, month, day, year, notes, private)

        # No need to get Event's row_id since we'll just reload Session.events
        self._execute(new_event_template, new_event)

    def update_event(self, event: Event) -> None:
        ''' Takes an event and any event field updates, and updates the event
            in the database.'''
        # Get event as how it's stored in the database, and make comparisons to the current
        # values of event. Collect changes and update event
        db_event = self.get_event(event.id)
        delta = lambda x, y: x != y
        updates = []

        def add_update(field, value) -> str:
            if type(value) == int:
                update = "UPDATE events SET {} = {} where event_id = {}".format(field, value, event.id)
            else:
                update = "UPDATE events SET {} = '{}' where event_id = {}".format(field, value, event.id)
            updates.append(update)

        # God this is a mess
        if delta(db_event.title, event.title):
            add_update('title', event.title)
        if delta(db_event.month, event.month):
            add_update('month', event.month)
        if delta(db_event.day, event.day):
            add_update('day', event.day)
        if delta(db_event.year, event.year):
            add_update('year', event.year)
        if delta(db_event.notes, event.notes):
            add_update('notes', event.notes)
        if delta(db_event.private, event.private):
            add_update('private', event.private)

        for update in updates:
            self._execute(update)

    def delete_event(self, event: Event) -> None:
        ''' Deletes an Event from the database. '''
        eid = (event.id,)
        self._execute("DELETE FROM events WHERE event_id = ? LIMIT 1", eid)

    def delete_calendar_events(self, calendar: Calendar) -> None:
        ''' Deletes all of a Calendar's Events from the database. '''
        cid = (calendar.id,)
        self._execute("DELETE FROM events WHERE calendar_id = ?", cid)
