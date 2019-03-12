''' Exceptions for use throughout the application '''

class UserNotFoundException(Exception):
    ''' User was not found in the database. '''
    pass

class LoginFailureException(Exception):
    ''' Password verification failed. '''
    pass