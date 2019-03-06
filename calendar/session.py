from typing import List
from sqlite3 import Connection
from sqlite3 import Error as SqliteError

from .classes import Calendar, User, Event
from .backend import Database

# TODO:
# * Finish sync_user_changes once backend.Database.update_user() is fixed
# * Add read-only functions to ShareSession

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

    def new_share_url(self):
        ''' Generate a new share URL for a Calendar. Calendars accessed through the 
            share URL will have all private events stripped. '''
        self.calendar.generate_share_url()

        # If the update doesn't meet the UNIQUE constraint on share_url, generate a new one
        while True:
            try:
                self.db.update_calendar_share_url(self.calendar)
                break
            except SqliteError:
                self.calendar.generate_share_url()

    def new_event(self, title, month, day, year=None, notes=None, private=0):
        ''' Create new event. '''
        cid = self.calendar.id
        self.db.insert_event(cid, title, month, day, year, notes, private)
        self.reload_events() # sync back up with database

    # Read methods

    def get_month_events(self, month: int) -> List[Event]:
        ''' Select all entries in self.events in the same month '''
        return [event for event in self.events if event.month == month]

    def reload_events(self) -> None:
        ''' Reload self.events with any new/updated Events. '''
        self.events = self.db.get_all_events(self.calendar.id)
    
    # Update syncing

    #def sync_user_changes(self):
    #    ''' Sync changes to a User with the database. Takes a User. '''
    #    self.db.update_user(self.user)

    def sync_event_changes(self, event: Event):
        ''' Sync changes to an event with the database. Takes an Event. '''
        self.db.update_event(event)
        self.reload_events() # sync any changes with self.events

    # Delete methods. Proceed with caution

    def remove_share_url(self):
        ''' Remove share URL for Calendar. '''
        # We can reuse the db method cuz it updates the value to NULL. Sweet
        self.calendar.remove_share_url()
        self.db.update_calendar_share_url(self.calendar)

    def remove_event(self, event: Event):
        ''' Removes an event from the database and from self.events '''
        event_index = self.events.index(event)
        self.db.delete_event(event)
        self.events.pop(event_index)

    def delete_account(self, confirm=False):
        ''' Deletes user account and all data associated with it. Confirm required. '''
        if confirm:
            # Delete from database in reverse order
            self.db.delete_calendar_events(self.calendar)
            self.db.delete_calendar(self.calendar)
            self.db.delete_user(self.user)
            
            # Delete object attributes
            delattr(self, 'user')
            delattr(self, 'calendar')
            delattr(self, 'events')


class ShareSession:
    def __init__(self, database, share_url):
        self.db = Database(database)
        self.calendar = self.db.get_calendar_by_share_url(share_url)
        self.events = self.db.get_all_events(self.calendar.id, strip_private=True)

    def get_month_events(self, month: int) -> List[Event]:
        ''' Select all entries in self.events in the same month '''
        return [event for event in self.events if event.month == month]