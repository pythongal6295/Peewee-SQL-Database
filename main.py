'''
This file stitches together functions from users and user_status objects.
'''
import csv
from os import path
from loguru import logger
import users
import user_status
import socialnetwork_model as snm

# user.none needs to be changed to none

#pylint: disable=C0103
def init_user_collection():
    '''
    Creates and returns a new instance
    of UserCollection
    '''
    new_collection = users.UserCollection()
    return new_collection

def init_status_collection():
    '''
    Creates and returns a new instance
    of UserStatusCollection
    '''
    new_collection = user_status.UserStatusCollection()
    return new_collection

def add_user(user_id, email, user_name, user_last_name, user_collection):
    '''
    Creates a new instance of User and stores it in user_collection
    (which is an instance of UserCollection)
    '''
    return user_collection.add_user(user_id, email,
                                    user_name, user_last_name)

def load_users(filename, user_collection):
    '''
    Opens a CSV file with user data and
    adds it to an existing instance of
    UserCollection

    Requirements:
    - If a user_id already exists, it
    will ignore it and continue to the
    next.
    - Returns False if there are any errors
    (such as empty fields in the source CSV file)
    - Otherwise, it returns True.
    '''

    if path.isfile(filename):
        print('File exists')
        logger.info(f'{filename} exits.')
    else:
        print('File does not exist yet.')
        logger.info(f'{filename} does not exist.')
        return False

    with open(filename, 'r') as file:
        #reads the header
        file.readline()
        raw_user_lst = csv.reader(file)
        user_lst = []
        for user in raw_user_lst:
            new_user = user_collection.database(user_id=user[0],
                          user_name=user[1],
                          user_last_name=user[2],
                          user_email=user[3])
            logger.info(new_user)
            user_lst.append(new_user)
        #Tried to make the above code a list comprehension, but there is a bug
        #[user_lst.append(user_collection.database(user_id = user[0],
                            #user_name = user[1], user_last_name = user[2],
                            #email = user[3])) for user in csv.reader(file)]
        #logger.info(type(user_lst))
        #logger.info(type(user_collection.database))
        logger.info('Created user list from file')
        #logger.info(user_lst[0])
    try:
        with snm.db.atomic():
            user_collection.database.bulk_create(user_lst, batch_size=100)
            logger.info('User table created.')
    except TypeError as e:
        logger.info('Error creating user table')
        logger.info(e)
        return False
    logger.info('User table created.')

    return True

def search_status(status_id, status_collection):
    '''
    Searches for a status in status_collection
    '''
    if isinstance(status_collection, user_status.UserStatusCollection):
        search_result = status_collection.search_status(status_id)
        return search_result
    raise AttributeError('Not a valid user collection')

def add_status(status_id, user_id, status_text, status_collection):
    '''
    Creates a new instance of UserStatus and stores it in user_collection
    (which is an instance of UserStatusCollection)
    '''
    return status_collection.add_status(status_id, user_id, status_text)

def load_status_updates(filename, status_collection):
    '''
    Opens a CSV file with status data and
    adds it to an existing instance of
    UserStatusCollection
    '''

    if path.isfile(filename):
        print('File exists')
        logger.info(f'{filename} exits.')
    else:
        print('File does not exist yet.')
        logger.info(f'{filename} does not exist.')
        return False

    with open(filename, 'r') as file:
        #reads the header
        file.readline()
        raw_status_lst = csv.reader(file)
        status_lst = []
        for status in raw_status_lst:
            new_status = status_collection.database(status_id=status[0],
                          user_id=status[1],
                          status_text=status[2])
            logger.info(new_status)
            status_lst.append(new_status)
        #logger.info(type(status_lst))
        #logger.info(type(status_collection.database))
        logger.info('Created status list from file')
        #logger.info(status_lst[0])
    try:
        with snm.db.atomic():
            status_collection.database.bulk_create(status_lst, batch_size=100)
            logger.info('Status table created.')
    except TypeError as e:
        logger.info('Error creating status table')
        logger.info(e)
        return False
    logger.info('Status table created.')

    return True


def update_user(user_id, email, user_name, user_last_name, user_collection):
    '''
    Updates the values of an existing user
    '''
    return user_collection.modify_user(user_id, email,
                                       user_name, user_last_name)

def delete_user(user_id, user_collection):
    '''
    Deletes a user from user_collection.
    '''
    return user_collection.delete_user(user_id)

def search_user(user_id, user_collection):
    '''
    Searches for a user in user_collection
    (which is an instance of UserCollection).
    '''
    if isinstance(user_collection, users.UserCollection):
        search_result = user_collection.search_user(user_id)
        return search_result
    raise AttributeError('Not a valid user collection')

def update_status(status_id, user_id, status_text, status_collection):
    '''
    Updates the values of an existing status_id
    '''
    return status_collection.modify_status(status_id, user_id, status_text)

def delete_status(status_id, status_collection):
    '''
    Deletes a status_id from user_collection.
    '''
    return status_collection.delete_status(status_id)


def search_all_status_updates(user_id, status_collection):
    '''
    Searches for a specific user_id and returns all the statuses for that person
    '''
    return status_collection.search_all_status_updates(user_id)

def filter_status_by_string(search_string, status_collection):
    '''
    searches database for all status updates that contain a word or phrase inputted by the user
    '''
    return status_collection.filter_status_by_string(search_string)
