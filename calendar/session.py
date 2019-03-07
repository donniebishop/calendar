from typing import List
from sqlite3 import Connection
from sqlite3 import Error as SqliteError

from .classes import Calendar, User, Event
from .backend import Repository

# TODO:
# * Finish sync_user_changes once backend.Database.update_user() is fixed
# * Add read-only functions to ShareSession

class Session:
    ''' Object to contain a session. '''
    def __init__(self, database, username, password):
        self.repo = Repository(database)
        self.user: User
        self.calendar: Calendar
        self.events: List[Event]

    def login(self, username, password):
        user = self.repo.users.get_user(username).pw_hash
        pw_hash = user.pw_hash
        login_success = self.repo.users.verify_password(password, pw_hash)

        if login_success:
            self.user = user
            self.calendar = self.repo.calendars.get_calendar_by_user_id(self.user.id)
            self.events = self.repo.events.get_all_events(self.calendar.id)

    def new_user(self, username, password, email=None):
        self.repo.users.insert_user(username, password, email)

    def new_share_url(self):
        ''' Generate a new share URL for a Calendar. Calendars accessed through the 
            share URL will have all private events stripped. '''
        self.calendar.generate_share_url()

        # If the update doesn't meet the UNIQUE constraint on share_url, generate a new one
        while True:
            try:
                self.repo.calendars.update_calendar_share_url(self.calendar)
                break
            except SqliteError:
                self.calendar.generate_share_url()

    def new_event(self, title, month, day, year=None, notes=None, private=0):
        ''' Create new event. '''
        cid = self.calendar.id
        self.repo.events.insert_event(cid, title, month, day, year, notes, private)
        self.reload_events() # sync back up with database

    # Read methods

    def get_month_events(self, month: int) -> List[Event]:
        ''' Select all entries in self.events in the same month '''
        return [event for event in self.events if event.month == month]

    def reload_events(self) -> None:
        ''' Reload self.events with any new/updated Events. '''
        self.events = self.repo.events.get_all_events(self.calendar.id)
    
    # Update syncing

    #def sync_user_changes(self):
    #    ''' Sync changes to a User with the database. Takes a User. '''
    #    self.db.update_user(self.user)

    def sync_event_changes(self, event: Event):
        ''' Sync changes to an event with the database. Takes an Event. '''
        self.repo.events.update_event(event)
        self.reload_events() # sync any changes with self.events

    # Delete methods. Proceed with caution

    def remove_share_url(self):
        ''' Remove share URL for Calendar. '''
        # We can reuse the db method cuz it updates the value to NULL. Sweet
        self.calendar.remove_share_url()
        self.repo.calendars.update_calendar_share_url(self.calendar)

    def remove_event(self, event: Event):
        ''' Removes an event from the database and from self.events '''
        event_index = self.events.index(event)
        self.repo.events.delete_event(event)
        self.events.pop(event_index)

    def delete_account(self, confirm=False):
        ''' Deletes user account and all data associated with it. Confirm required. '''
        if confirm:
            # Delete from database in reverse order
            self.repo.events.delete_calendar_events(self.calendar)
            self.repo.calendars.delete_calendar(self.calendar)
            self.repo.users.delete_user(self.user)
            
            # Delete object attributes
            delattr(self, 'user')
            delattr(self, 'calendar')
            delattr(self, 'events')


class ShareSession:
    def __init__(self, database: str, share_url: str):
        self.repo = Repository(database)
        self.calendar = self.repo.calendars.get_calendar_by_share_url(share_url)
        self.events = self.repo.events.get_all_events(self.calendar.id, strip_private=True)

    def get_month_events(self, month: int) -> List[Event]:
        ''' Select all entries in self.events in the same month '''
        return [event for event in self.events if event.month == month]
