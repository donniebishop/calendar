from typing import List
from sqlite3 import Connection

from classes import Calendar, User, Event
from backend import Database

def new_user(db: Database, username, password, email=None) -> User:
    db.new_user(username, password, email)

class Session:
    ''' Object to contain a session. '''
    def __init__(self, db: Database, username, password):
        self.db = db
        self.connection: Connection = self.db.connection
        self.user: User
        self.calendar: Calendar
        self.events: List[Event]

        if self.login(username, password):
            self.user = self.db.get_user(username)
            self.calendar = self.db.get_calendar(self.user.calendar_id)
            self.events = self.db.get_all_events(self.calendar.id)

    def login(self, username, password) -> bool:
        pw_hash = self.db.get_user(username).pw_hash
        return self.db.verify_password(password, pw_hash)

    def new_event(self, title, month, day, year=None, notes=None):
        ''' Create new event. '''
        event_id = self.db.insert_event(title, month, day, year, notes)
        event = self.db.get_event(event_id)
        self.events.append(event)

    #def update_event(title, month, day, year=None, notes=None, private=0):
