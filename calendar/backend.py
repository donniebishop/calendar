#!/usr/bin/env python3

import sqlite3
from passlib.hash import pbkdf2_sha256 as pbkdf2
from typing import List, Tuple

# Custom imports
from classes import User, Calendar, Event

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
        if not self.connection:
            return sqlite3.connect(self.name)

    def _get_cursor(self) -> sqlite3.Cursor:
        ''' Returns a Cursor object from the Connection object. '''
        if self.connection and not self.cursor:
            return self.connection.cursor()

    def _get_result(self):
        ''' Return first cursor result. '''
        if self.connection and self.cursor:
            self.connection.commit()
            return self.cursor.fetchone()
        
    def _get_all_results(self):
        ''' Return all cursor results. '''
        if self.connection and self.cursor:
            self.connection.commit()
            return self.cursor.fetchall()

    def _get_lastrowid(self) -> int:
        if self.cursor:
            self.cursor.lastrowid

    def _execute(self, sql_template, sql_tuple=None) -> None:
        ''' Shortcut for self.cursor.execute(). '''
        self.cursor.execute(sql_template, sql_tuple)

    def _close_all(self) -> None:
        ''' Close Cursor and Connection objects. '''
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    # Select methods
    def get_user(self, user_id: int) -> User:
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

    def get_events_by_calendar(self, calendar_id: int) -> List[Event]:
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
    def new_user(self, username, password, email=None):
        ''' Inserts a new User into the users table. Returns the user_id of the new User. '''
        new_user_template = "INSERT INTO users (username, pw_hash, email) \
                             VALUES (?,?,?)"
        password_hash = pbkdf2.hash(str(password))
        new_user: Tuple = (username, password_hash, email)

        self._execute(new_user_template, new_user)
        return self._get_lastrowid()

    def new_event(self, calendar_id, title, month, day, year=None, notes=None, private=None):
        ''' Inserts a new Event into the events table. Returns event_id of the new Event. '''
        new_event_template = "INSERT INTO events (calendar_id, title, month, day, year, notes, private) \
                              VALUES(?,?,?,?,?,?,?)"
        new_event: Tuple = (calendar_id, title, month, day, year, notes, private)

        self._execute(new_event_template, new_event)
        return self._get_lastrowid()
        
    # Update methods
    def update_user(self):
        pass

    def update_event(self, event_id):
        #update_event = "UPDATE events
        #                SET event"
        #event_tuple = (event.id, event.month, event.day, event.year, event.notes)
        pass