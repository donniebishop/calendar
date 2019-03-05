from passlib.hash import pbkdf2_sha256 as pbkdf2

class User():
    ''' Object to represent an entry from the users table. User's calendar
        is retrieved based on the user's calendar_id. '''
    def __init__(self, user_id, username, pw_hash, email=None):
        self.id = user_id
        self.username = username
        self.pw_hash = pw_hash
        self.email = email

    def change_password(self, password) -> None:
        ''' Create a new pw_hash and replace the old hash. '''
        self.pw_hash = pbkdf2.hash(str(password))

    def change_email(self, email) -> None:
        ''' Add or update email address associated with user. '''
        self.email = email

    def remove_email(self) -> None:
        ''' Remove email associated with the user. '''
        self.email = None

class Calendar():
    '''Represents an entry from the calendars table. Events with a matching
       calendar_id are stored in the self.events list.'''
    def __init__(self, calendar_id, user_id, share_url=None):
        self.id = calendar_id
        self.user_id = user_id
        self.share_url = share_url

    def generate_share_url(self):
        if not self.share_url:
            pass

    # def new_event(self, db: Database, title, month, day, year=None, notes=None):
    #     event_id = db.insert_event(self.id, title, month, day, year, notes)
    #     db.get_event(event_id)


class Event():
    '''Represents an entry from the events table.'''
    def __init__(self, event_id, calendar_id, title, month, day,
                 year=None, notes=None, private=0):
        self.id = event_id
        self.calendar_id = calendar_id
        self.title = title
        self.month = month
        self.day = day
        self.year = year
        self.notes = notes
        self.private = private # No BOOL type. Must be integer. 0 = False, 1 True

    def __repr__(self):
        return str("[{}, {}, {}, {}]".format(self.id, self.month, self.day, self.title))

    def update_title(self, title=None):
        if title:
            self.title = str(title)

    def update_date(self, month=None, day=None, year=None):
        if month:
            self.month = int(month)
        if day:
            self.day = int(day)
        if year:
            self.year = int(year)

    def update_notes(self, notes=None):
        ''' Update notes field of event. '''
        if notes:
            self.notes = str(notes)

    def update_private(self, private=None):
        ''' Update private field of event. Note that private must be an int.
            0 for False, 1 for True. '''
        if private:
            self.private = int(private)
