

class Base:

    def __init__(self, user):
        self.user = user

    def verify_authorization():
        #in future, this will run in every request 
        #to verify if the person trying to view the data
        #is authorized
        pass

    def log_view():
        #in future, will write to database
        # who looked at what, when
        pass