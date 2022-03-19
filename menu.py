'''
Provides a basic frontend
'''
import sys
from datetime import date
from loguru import logger
import main
import socialnetwork_model as sm


#pylint: disable=C0103

logger.remove()
logger.add('log_' + str(date.today()) + '.log')

def load_users():
    '''
    Loads user accounts from a file
    '''
    filename = input('Enter filename of user file: ')
    main.load_users(filename, user_collection)
    print('File data has been uploaded.')

def load_status_updates():
    '''
    Loads status updates from a file
    '''
    filename = input('Enter filename for status file: ')
    main.load_status_updates(filename, status_collection)
    print('Status data has been uploaded.')

def add_user():
    '''
    Adds a new user into the database
    '''
    user_id = input('User ID: ')
    email = input('User email: ')
    user_name = input('User name: ')
    user_last_name = input('User last name: ')
    if not main.add_user(user_id, email, user_name, user_last_name, user_collection):
        print("An error occurred while trying to add new user")
    else:
        print("User was successfully added")

def update_user():
    '''
    Updates information for an existing user
    '''
    user_id = input('User ID: ')
    email = input('User email: ')
    user_name = input('User name: ')
    user_last_name = input('User last name: ')
    if not main.update_user(user_id, email, user_name, user_last_name,
                            user_collection):
        print("An error occurred while trying to update user")
    else:
        print("User was successfully updated")

def search_user():
    '''
    Searches a user in the database
    '''
    user_id = input('Enter user ID to search: ')
    result = main.search_user(user_id, user_collection)
    if result is None:
        print("ERROR: User does not exist")
    else:
        print(f"User ID: {result.user_id}")
        print(f"Email: {result.user_email}")
        print(f"Name: {result.user_name}")
        print(f"Last name: {result.user_last_name}")

def delete_user():
    '''
    Deletes user from the database
    '''
    user_id = input('User ID: ')
    if not main.delete_user(user_id, user_collection):
        print("An error occurred while trying to delete user")
    else:
        print("User was successfully deleted")


def add_status():
    '''
    Adds a new status into the database
    '''
    user_id = input('User ID: ')
    status_id = input('Status ID: ')
    status_text = input('Status text: ')
    if not main.add_status(status_id, user_id, status_text, status_collection):
        print("An error occurred while trying to add new status")
    else:
        print("New status was successfully added")

def update_status():
    '''
    Updates information for an existing status
    '''
    user_id = input('User ID: ')
    status_id = input('Status ID: ')
    status_text = input('Status text: ')
    if not main.update_status(status_id, user_id, status_text, status_collection):
        print("An error occurred while trying to update status")
    else:
        print("Status was successfully updated")

def search_status():
    '''
    Searches a status in the database
    '''
    status_id = input('Enter status ID to search: ')
    result = main.search_status(status_id, status_collection)
    if result is None:
        print("ERROR: Status does not exist")
    else:
        print(f"User ID: {result.user_id}")
        print(f"Status ID: {result.status_id}")
        print(f"Status text: {result.status_text}")

def delete_status():
    '''
    Deletes status from the database
    '''
    status_id = input('Status ID: ')
    if not main.delete_status(status_id, status_collection):
        print("An error occurred while trying to delete status")
    else:
        print("Status was successfully deleted")

def search_all_status_updates():
    '''
    Searches for all the statuses associated with a specific user_id
    '''
    user_id = input('User ID: ')
    query = main.search_all_status_updates(user_id, status_collection)
    #logger.info(query[0])

    if not query:
        print('An error occured while trying to search all status updates.')
    else:
        print('A total of ', len(query), f'status updates are found for {user_id}')
        iter_query = iter(query)
        while True:
            next_choice = input('Would you like to see the next update? (Y/N)? ')
            if next_choice.upper() == 'Y':
                try:
                    next_item = next(iter_query)
                except StopIteration:
                    logger.warning('Iteration has run out of entries.')
                    print('There are no more status updates.')
                    return False
                print(next_item.status_text)
                logger.info(f'Item in query: {next_item}')
            else:
                return False
            continue
    return True

#@pysnooper.snoop()
def filter_status_by_string():
    '''
    searches database for all status updates that contain a word or phrase inputted by the user
    '''
    search_string = input('Enter a word or phrase to search by: ')
    query = main.filter_status_by_string(search_string, status_collection)

    if not query:
        logger.error('An error occured while trying to search or there were no results.')
        print('There are no results with that search or there was an error.')
    else:
        print('Here are the results: ')
        while True:
            next_choice = input('Would you like to see the next update? (Y/N) ')
            if next_choice.upper() == 'Y':
                try:
                    next_item = next(query)
                    logger.info('next item', next_item)
                except StopIteration:
                    logger.warning('Iteration has run out of entries.')
                    print('There are no more status updates.')
                    return False
                print(next_item.status_text)
                logger.info(f'Item in query: {next_item}')
            else:
                return False
            continue
    return True

def flagged_status_updates():
    '''
    Searches status updates based on a user inputted string and returns a tuple of results
    '''
    search_string = input('Enter a word or phrase to search by: ')
    query = main.filter_status_by_string(search_string, status_collection)
    if not query:
        logger.error('An error occured while trying to search or there were no results.')
        print('There are no results with that search or there was an error.')
    else:
        print('Here are the results: ')
        # This code works, but is not a list comprehension
        # while True:
        #     try:
        #         next_item = next(query)
        #         logger.info('next item:', next_item)
        #     except StopIteration:
        #         logger.warning('Iteration has run out of entries.')
        #         return False
        #     print((next_item.status_id, next_item.status_text))
        #     continue

        # Attempt #1 at a list comprehension
        # while True:
        #     try:
                # next_item = next(query)
                # query_tpl = [(next_item.status_id, next_item.status_text) for next_item.status_id in next_item for next_item.status_text in next_item]
                # print(query_tpl)

        #Attempt #2 at a list comprehension
        query_list = []
        for status in (item for item in query):
            query_list.append((status.status_id, status.status_text))
        print(query_list)

#My start at a generator function. These are still confusing to me.
# def status_generator(query, user_id):
#     '''
#     creates a generator for a query
#     '''
#     query_len = len(query)
#     print('A total of ', query_len, f'status updates are found for {user_id}')
#     i = query_len
#     while i > 0:

def quit_program():
    '''
    Quits program
    '''
    sys.exit()

if __name__ == '__main__':
    sm.main()
    user_collection = main.init_user_collection()
    status_collection = main.init_status_collection()
    menu_options = {
        'A': load_users,
        'B': load_status_updates,
        'C': add_user,
        'D': update_user,
        'E': search_user,
        'F': delete_user,
        'G': add_status,
        'H': update_status,
        'I': search_status,
        'J': delete_status,
        'K': search_all_status_updates,
        'L': filter_status_by_string,
        'M': flagged_status_updates,
        'Q': quit_program
    }
    while True:
        user_selection = input("""
                            A: Load user database
                            B: Load status database
                            C: Add user
                            D: Update user
                            E: Search user
                            F: Delete user
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Delete status
                            K: Search all status updates
                            L: Search all status updates by a string
                            M: Show all flagged status updates
                            Q: Quit

                            Please enter your choice: """)
        if user_selection.upper() in menu_options:
            menu_options[user_selection.upper()]()
        else:
            print("Invalid option")
