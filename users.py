'''
Classes for user information for the
social network project
'''
# pylint: disable=R0903,  E0401
from loguru import logger
import peewee as pw
import socialnetwork_model as sm


class UserCollection():
    '''
    Contains a collection of Users objects
    '''
    def __init__(self):
        self.database = sm.Users

    def add_user(self, user_id, email, user_name, user_last_name):
        '''
        Adds a new user to the collection
        '''
        try:
            self.database.create(user_id=user_id,
                                 user_email=email,
                                 user_name=user_name,
                                 user_last_name=user_last_name)
            logger.info("User successfully added")
            return True
        except pw.IntegrityError:
            logger.warning("This user already exists.")
            return False

    def modify_user(self, user_id, email, user_name, user_last_name):
        '''
        Modifies an existing user
        '''
        try:
            modify = self.database.get_by_id(user_id)
            (modify.update({self.database.user_email: email,
                            self.database.user_name: user_name,
                            self.database.user_last_name: user_last_name}).\
                            where(self.database.user_id == user_id).execute())
            logger.info("User ID {} modified to have email {},"
                        "first_name {} and last_name {}",
                        user_id, email, user_name, user_last_name)
            return True
        except pw.DoesNotExist:
            logger.warning("User cannot be modified as it doesn't exist.")
            return False

    def delete_user(self, user_id):
        '''
        Deletes an existing user
        '''
        try:
            self.database.get_by_id(user_id).delete_instance()
            logger.info("User_id {} successfully deleted", user_id)
            return True
        except pw.DoesNotExist:
            logger.warning("User cannot be deleted as it doesn't exist.")
            return False

    def search_user(self, user_id):
        '''
        Searches for user data
        '''
        try:
            return_value = self.database.get_by_id(user_id)
            logger.info("User_ID {} found.", user_id)
            return return_value
        except pw.DoesNotExist:
            logger.warning("User not found")
            return None
