from flask import Flask
from flask_restful import Api, Resource, abort

from backend import Repository
from exceptions import *

app = Flask(__name__)
api = Api(app)
repo = Repository('test.db')

# utilities
def serialize_user(user):
    return {'id': user.id, 'username': user.username, 'email': user.email}

def serialize_event(event):
    return {
            'id': event.id,
            'title': event.title,
            'month': event.month,
            'day': event.day,
            'year': event.year,
            'notes': event.notes,
            'private': event.private
        }

# API methods
class UserAPI(Resource):
    def get(self, user_id):
        try:
            user = repo.users.get_user_by_id(user_id)
            return serialize_user(user)
        except UserNotFoundException:
            abort(404, message='User ID {} not found.'.format(user_id))

class EventAPI(Resource):
    def get(self, event_id):
        try:
            event = repo.events.get_event(event_id)
            return serialize_event(event)
        except EventNotFoundException:
            abort(404, message='Event ID {} not found.'.format(event_id))

class UserEventsAPI(Resource):
    def get(self, user_id):
        cal = repo.calendars.get_calendar_by_user_id(user_id)
        events = repo.events.get_all_events(cal.id)
        return [serialize_event(e) for e in events]

# API endpoints
api.add_resource(UserAPI, '/user/<user_id>')
api.add_resource(UserEventsAPI, '/user/<user_id>/events')
api.add_resource(EventAPI, '/event/<event_id>')

if __name__ == '__main__':
    app.run(debug=True)