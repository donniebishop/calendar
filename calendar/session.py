from typing import List
from sqlite3 import Connection

from .classes import Calendar, User, Event
from .backend import Database

class Session:
    ''' Object to contain a session. '''
    def __init__(self, database, username, password, new_user=False):
        self.db = Database(database)
        self.connection: Connection = self.db.connection
        self.user: User
        self.calendar: Calendar
        self.events: List[Event]

        if new_user:
            # Create new entries
            uid = self.db.insert_user(username, password)
            cid = self.db.insert_calendar(uid)
            # return entries
            self.user = self.db.get_user_by_id(uid)
            self.calendar = self.db.get_calendar(cid)
            self.events = []
        elif self.login(username, password):
            self.user = self.db.get_user(username)
            self.calendar = self.db.get_calendar_by_user_id(self.user.id)
            self.events = self.db.get_all_events(self.calendar.id)

    def login(self, username, password) -> bool:
        pw_hash = self.db.get_user(username).pw_hash
        return self.db.verify_password(password, pw_hash)

    def new_event(self, title, month, day, year=None, notes=None, private=0):
        ''' Create new event. '''
        cid = self.calendar.id
        event_id = self.db.insert_event(cid, title, month, day, year, notes, private)
        event = self.db.get_event(event_id)
        self.events.append(event)
    
    # Update syncing

    #def sync_user_changes(self):
    #    ''' Sync changes to a User with the database. Takes a User. '''
    #    self.db.update_user(self.user)

    def sync_event_changes(self, event: Event):
        ''' Sync changes to an event with the database. Takes an Event. '''
        # I love that all the work in the backend makes this so simple here
        self.db.update_event(event)

    #def update_event(title, month, day, year=None, notes=None, private=0):
