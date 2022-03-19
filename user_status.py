'''
Classes for user status information for the
social network project
'''
# pylint: disable=R0903, E0401
from loguru import logger
import peewee as pw
import socialnetwork_model as sm
#import more_itertools


class UserStatusCollection:
    '''
    Contains a collection of UserStatus objects
    '''

    def __init__(self):
        self.database = sm.Status

    def add_status(self, status_id, user_id, status_text):
        '''
        Adds a new user to the collection
        '''
        try:
            self.database.create(status_id=status_id,
                                 user_id=user_id,
                                 status_text=status_text)
            logger.info("Status successfully added")
            return True
        except pw.IntegrityError:
            logger.warning("Status not added, either a duplicate status ID"
                           " or missing required foreign key user_id.")


    def modify_status(self, status_id, user_id, status_text):
        '''
        Modifies an existing status
        '''
        try:
            modify = self.database.get_by_id(status_id)
            (modify.update({self.database.user_id: user_id,
                            self.database.status_text: status_text}).\
                            where(self.database.status_id == status_id).\
                            execute())
            logger.info("Status_id {} modified to have user_id {} "
                        "and status_text {}",
                        status_id, user_id, status_text)
            return True
        except pw.DoesNotExist:
            logger.warning("Status cannot be modified as it doesn't exist.")
            return False
        except pw.IntegrityError:
            logger.warning(
                "Cannot modify status to a user_id that does not exist.")
            return False

    def delete_status(self, status_id):
        '''
        Deletes an existing user
        '''
        try:
            self.database.get_by_id(status_id).delete_instance()
            logger.info("Status_id {} successfully deleted", status_id)
            return True
        except pw.DoesNotExist:
            logger.warning("Status cannot be deleted as it doesn't exist.")
            return False

    def search_status(self, status_id):
        '''
        Searches for user status data
        '''
        try:
            return_value = self.database.get_by_id(status_id)
            logger.info("Status_id {} found.", status_id)
            return return_value
        except pw.DoesNotExist:
            logger.warning("Status not found")
            return None


    def search_all_status_updates(self, user_id):
        '''
        Searches by a user_id and returns all status updates from that user
        '''
        try:
            query = self.database.select().where(self.database.user_id == user_id)
            logger.info(f'User_id {user_id} found. Returning status query.')
            return query
        except pw.DoesNotExist:
            logger.warning(f'User_id {user_id} not found.')
            return None

    def filter_status_by_string(self, search_string):
        '''
        searches database for all status updates that contain a word or phrase inputted by the user
        '''
        query = self.database.select().where(self.database.status_text.contains(search_string)).iterator()
        return query

        #I attempted to check to see if the query is empty
        #so it wouldn't go through the while loop in menu.py.
        # Instead menu.py would print that there are no results
        # size_check = more_itertools.peekable(list(query))

        # if size_check == True:
        #     logger.info(f'Found results based on {search_string}')
        #     logger.info(list(size_check))
        #     logger.info(query)
        #     return query
        # else:
        #     logger.info(f'No results based on search string: {search_string}')
        #     print('There are no results with that word or phrase.')
        #     return None
