#!/usr/bin/env python3

from typing import List
from passlib.hash import pbkdf2_sha256 as pbkdf2

class User:
    ''' Object to represent an entry from the users table. User's calendar
        is retrieved based on the user's calendar_id'''
    def __init__(self, user_id, username, email, pw_hash, calendar_id):
        self.id = user_id
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.calendar_id = calendar_id
        self.calendar: Calendar

    def verify_password(self, password):
        ''' Verifies password matches the password hash. '''
        return pbkdf2.verify(password, self.pw_hash)


class Calendar:
    '''Represents an entry from the calendars table. Events with a matching
       calendar_id are stored in the self.events list.'''
    def __init__(self, calendar_id, user_id, share_url=None):
        self.id = calendar_id
        self.user_id = user_id
        self.share_url = share_url
        self.events: List[Event] = []

    def generate_share_url(self):
        if not self.share_url:
            pass

    # def new_event(self, db: Database, title, month, day, year=None, notes=None):
    #     event_id = db.insert_event(self.id, title, month, day, year, notes)
    #     db.get_event(event_id)


class Event:
    '''Represents an entry from the events table.'''
    def __init__(self, event_id, calendar_id, title, month, day, year, notes):
        self.id = event_id
        self.calendar_id = calendar_id
        self.title = title
        self.month = month
        self.day = day
        self.year = year
        self.notes = notes

    def __repr__(self):
        return str("[{}, {}, {}, {}]".format(self.id, self.month, self.day, self.title))

    def update_title(self, title=None):
        if title:
            self.title = str(title)

    def update_date(self, month=None, day=None):
        if month:
            self.month = int(month)
        if day:
            self.day = int(day)

    def update_notes(self, notes=None):
        if notes:
            self.notes = str(notes)

