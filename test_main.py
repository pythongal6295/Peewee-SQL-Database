'''
The suite of unit tests for main.py, user_status.py, and users.py
'''
import os
from unittest import TestCase
import mock
import peewee as pw
import socialnetwork_model as sm
from users import UserCollection
from user_status import UserStatusCollection
import main as M

#pylint: disable=C0103
test_data = {'Bob': ['bob123', 'Bob', 'Belcher', 'bob123@gmail.com'],
             'Linda': ['linda123', 'Linda', 'Belcher', 'linda@gmail.com'],
             'Gene': ['gene234', 'Gene', 'Belcher', 'gene@gmail.com'],
             'Tina': ['tina345', 'Tina', 'Belcher', 'tina@gmail.com']}
status_data = {1: ['bob123__00001', 'bob123', 'I love burgers!'],
               2: ['bob123__00002', 'bob123', 'Jimmy Pesto sux!'],
               3: ['linda123__00001', 'linda123', "Oh like I'm not gonna sing"]}

class SocialNetworkModelTests(TestCase):
    '''
    Tests for the database setup file
    '''

    def setUp(self):
        '''
        Establishes DB connection for setup
        '''
        self.db = sm.db
        self.db.connect(reuse_if_open=True)

    def tearDown(self):
        '''
        Drops tables & closes db connection for teardown
        '''
        if self.db.table_exists('users'):
            self.db.drop_tables(sm.Users)
        if self.db.table_exists('status'):
            self.db.drop_tables(sm.Status)
        self.db.close()

    def test_users_table(self):
        '''
        Tests that users table is created with correct params
        '''
        sm.main()
        correct_cols = ['user_id', 'user_name', 'user_last_name', 'user_email']
        test_cols = [x[0] for x in self.db.get_columns('users')]
        pk = self.db.get_primary_keys('users')[0]
        self.assertEqual(test_cols, correct_cols)
        self.assertEqual('user_id', pk)

    def test_status_table(self):
        '''
        Tests that status table is created with correct params
        '''
        sm.main()
        correct_cols = ['status_id', 'user_id', 'status_text']
        test_cols = [x[0] for x in self.db.get_columns('status')]
        pk = self.db.get_primary_keys('status')[0]
        fk = self.db.get_foreign_keys('status')[0][0]
        self.assertEqual(test_cols, correct_cols)
        self.assertEqual('status_id', pk)
        self.assertEqual('user_id', fk)

    def test_create_tables(self):
        '''
        Tests that create_table function works as expected
        '''
        result = sm.create_tables(self.db, (sm.Users, sm.Status))
        self.assertTrue(result)
        self.assertTrue(self.db.table_exists('users'))
        self.assertTrue(self.db.table_exists('status'))


    def test_main(self):
        '''
        Tests that main function works as expected
        '''
        with mock.patch('socialnetwork_model.create_tables') as ct:
            result = sm.main()
            self.assertTrue(result)
        ct.assert_called_with(sm.db, (sm.Users, sm.Status))

class UsersTests(TestCase):
    '''
    The tests for all classes in the users.py file
    '''

    def setUp(self):
        self.db = pw.SqliteDatabase(':memory:')
        sm.main()
        self.users = UserCollection()

    def tearDown(self):
        self.db.drop_tables((sm.Users, sm.Status))
        self.db.close()

    def test_user_collection_init(self):
        '''
        Tests that a user collection object can be instantiated
        '''
        self.assertEqual(self.users.database, sm.Users)
        self.assertIsInstance(self.users, UserCollection)

    def test_add_user(self):
        '''
        Tests that add_user function works properly
        '''
        first_user = self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                                         test_data['Bob'][2], test_data['Bob'][3])
        self.assertTrue(first_user)
        self.assertEqual(self.users.database.get_by_id(\
                         test_data['Bob'][0]).user_id,
                         test_data['Bob'][0])
        same_user = self.users.add_user(test_data['Bob'][0],
                                        test_data['Bob'][1],
                                        test_data['Bob'][2],
                                        test_data['Bob'][3])
        self.assertFalse(same_user)
        second_user = self.users.add_user(test_data['Linda'][0],
                                          test_data['Linda'][1],
                                          test_data['Linda'][2],
                                          test_data['Linda'][3])
        self.assertTrue(second_user)
        self.assertEqual(self.users.database.\
                         get_by_id(test_data['Linda'][0]).user_id,
                         test_data['Linda'][0])

    def test_modify_user(self):
        '''
        Tests that you can modify a user's information
        '''
        #should return false when user doesn't exist
        self.assertFalse(self.users.modify_user(test_data['Bob'][0],
                                                test_data['Bob'][1],
                                                test_data['Bob'][2],
                                                test_data['Bob'][3]))
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])
        changed_bob = self.users.modify_user(test_data['Bob'][0],
                                             test_data['Gene'][1],
                                             test_data['Gene'][2],
                                             test_data['Gene'][3])
        self.assertTrue(changed_bob)
        bob_data = self.users.database['bob123']
        self.assertEqual(bob_data.user_email, test_data['Gene'][1])
        self.assertEqual(bob_data.user_name, test_data['Gene'][2])
        self.assertEqual(bob_data.user_last_name, test_data['Gene'][3])

    #pylint: disable=W0104
    def test_delete_user(self):
        '''
        Tests that you can delete a user
        '''
        # should return false when user doesn't exist
        self.assertFalse(self.users.delete_user(test_data['Gene'][0]))
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])
        del_user = self.users.delete_user(test_data['Bob'][0])
        self.assertTrue(del_user)
        with self.assertRaises(pw.DoesNotExist):
            self.users.database.get_by_id('bob123')

    def test_search_user(self):
        '''
        Tests that user search returns the right person
        '''
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])
        not_exists = self.users.search_user(test_data['Tina'][0])
        self.assertEqual(not_exists, None)
        self.assertEqual(self.users.search_user(test_data['Bob'][0]),
                         self.users.database['bob123'])


class UserStatusTests(TestCase):
    '''
    Class of unit tests for user_status.py
    '''

    def setUp(self):
        self.db = pw.SqliteDatabase(':memory:')
        sm.main()
        self.statuses = UserStatusCollection()
        self.users = UserCollection()
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])

    def tearDown(self):
        self.db.drop_tables((sm.Users, sm.Status))
        self.db.close()

    def test_status_collection_init(self):
        '''
        Tests that a user status collection may be instantiated
        '''
        self.assertEqual(self.statuses.database, sm.Status)
        self.assertIsInstance(self.statuses, UserStatusCollection)

    def test_add_status(self):
        '''
        Tests that a user status may be added to a collection
        '''
        first_status = self.statuses.add_status(status_data[1][0],
                                                status_data[1][1],
                                                status_data[1][2])
        self.assertTrue(first_status)
        self.assertEqual(self.statuses.database.\
                         get_by_id(status_data[1][0]).status_id,
                         status_data[1][0])
        same_status = self.statuses.add_status(status_data[1][0],
                                               status_data[1][1],
                                               status_data[1][2])
        self.assertFalse(same_status)
        # can add another status for a user that exists
        second_status = self.statuses.add_status(status_data[2][0],
                                                 status_data[2][1],
                                                 status_data[2][2])
        self.assertTrue(second_status)
        self.assertEqual(self.statuses.database.\
                         get_by_id(status_data[2][0]).status_id,
                         status_data[2][0])
        # cannot add another status for a user that does not exist
        second_status = self.statuses.add_status(status_data[3][0],
                                                 status_data[3][1],
                                                 status_data[3][2])
        self.assertFalse(second_status)

    def test_modify_status(self):
        '''
        Tests that a user status may be modified
        '''
        self.statuses.add_status(status_data[1][0],
                                 status_data[1][1],
                                 status_data[1][2])
        #should return false when status ID not in database
        self.assertFalse(self.statuses.modify_status(status_data[3][0],
                                                     status_data[3][1],
                                                     status_data[3][2]
                                                     ))
        # should return false when the user is not in the users table
        nonexistent_user = self.statuses.modify_status(status_data[1][0],
                                                       status_data[3][1],
                                                       status_data[3][2])
        self.assertFalse(nonexistent_user)
        #should work when status ID exists & user ID in users table
        changed_status = self.statuses.modify_status(status_data[1][0],
                                                     status_data[1][1],
                                                     status_data[3][2])
        self.assertTrue(changed_status)
        changed_status = self.statuses.database.get_by_id([status_data[1][0]])
        self.assertEqual(changed_status.user_id.user_id, status_data[1][1])
        self.assertEqual(changed_status.status_text, status_data[3][2])

    #pylint: disable=W0104
    def test_delete_status(self):
        '''
        Tests that a user status may be deleted
        '''
        self.statuses.add_status(status_data[1][0],
                                 status_data[1][1],
                                 status_data[1][2])
        del_status = self.statuses.delete_status(status_data[1][0])
        self.assertTrue(del_status)
        self.assertFalse(self.statuses.delete_status(status_data[1][0]))
        with self.assertRaises(pw.DoesNotExist):
            self.statuses.database.get_by_id(status_data[1][0])

    def test_search_status(self):
        '''
        Tests that a status search returns the right status
        '''
        self.statuses.add_status(status_data[1][0],
                                 status_data[1][1],
                                 status_data[1][2])
        not_exists = self.statuses.search_status(status_data[2][0])
        self.assertEqual(not_exists, None)
        self.assertEqual(self.statuses.search_status(status_data[1][0]).\
                         status_id,
                         status_data[1][0])

class MainTests(TestCase):
    '''
    Tests the functions from main.py
    '''

    def setUp(self):
        self.db = pw.SqliteDatabase(':memory:')
        sm.main()
        self.users = UserCollection()
        self.statuses = UserStatusCollection()


    def test_init_user_collection(self):
        '''
        Tests that init_user_collection returns a new user collection
        '''
        users = M.init_user_collection()
        self.assertIsInstance(users, UserCollection)
        self.assertEqual(users.database, sm.Users)

    def test_init_status_collection(self):
        '''
        Tests that init_status_collection returns a new status collection
        '''
        statuses = M.init_status_collection()
        self.assertIsInstance(statuses, UserStatusCollection)
        self.assertEqual(statuses.database, sm.Status)

    @mock.patch('main.add_user')
    def test_load_users(self, mock_add_user):
        '''
        Tests that load_users has expected behavior for new users,
        existing users, missing files, and malformed input data
        '''
        test_file_name = 'load_users_test.csv'
        header = 'user_id, name, last_name, email'
        bob = ','.join(test_data['Bob'])
        bad_data = ','.join(['only', 'two columns'])

        #creates test file for first use case
        file_test = '\n'.join([header, bob, bob])
        with open(test_file_name, 'w') as f:
            f.write(file_test)

        #tests that search_user is called with the right fields
        #tests that add user is called with right fields when search return none
        #tests that add user is not called when search returns not none
        with mock.patch('main.search_user',
                        side_effect=[None, 'Not None']) as srch:
            self.assertTrue(M.load_users(test_file_name, self.users))
            kwargs = {'user_id': test_data['Bob'][0],
                      'user_name': test_data['Bob'][1],
                      'user_last_name': test_data['Bob'][2],
                      'email': test_data['Bob'][3],
                      'user_collection': self.users}
            mock_add_user.assert_called_once_with(**kwargs)
            srch.assert_called_with(test_data['Bob'][0], self.users)

        #creates test file for second use case testing bad input
        file_test = '\n'.join([header, bad_data])
        with open(test_file_name, 'w') as f:
            f.write(file_test)

        self.assertFalse(M.load_users(test_file_name, self.users))

        # checks that the file not found error is raised
        with self.assertRaises(FileNotFoundError):
            M.load_users('fake.txt', self.users)

    def test_save_users(self):
        '''
        Tests that save files pass and fails as expected
        '''
        good = 'save_users_test.csv'
        bad = 'bad'
        self.users.add_user(test_data['Bob'][0],
                            test_data['Bob'][1],
                            test_data['Bob'][2],
                            test_data['Bob'][3])
        self.assertTrue(M.save_users(good, self.users))
        self.assertTrue(os.path.exists(good))
        self.assertFalse(M.save_users('bad', self.users))
        self.assertFalse(os.path.exists(bad))

    @mock.patch('main.add_status')
    def test_load_status_updates(self, mock_add_status):
        '''
        Tests that load_status_updates has expected behavior for new statuses,
        existing statuses, missing files, and malformed input data
        '''
        test_file_name = 'load_statuses_test.csv'
        header = 'status_id, user_id, status_text'
        bob = ','.join(status_data[1])
        bad_data = ','.join(['only', 'two columns'])

        # creates test file for first use case
        file_test = '\n'.join([header, bob, bob])
        with open(test_file_name, 'w') as f:
            f.write(file_test)

        with mock.patch('main.search_status', side_effect=[None, 'Not None']) as srch:
            self.assertTrue(M.load_status_updates(test_file_name,
                                                  self.statuses))
            mock_add_status.assert_called_once_with(status_data[1][0],
                                                    status_data[1][1],
                                                    status_data[1][2],
                                                    self.statuses)
            srch.assert_called_with(status_data[1][0], self.statuses)

        # creates test file for second use case testing bad input
        file_test = '\n'.join([header, bad_data])
        with open(test_file_name, 'w') as f:
            f.write(file_test)

        self.assertFalse(M.load_status_updates(test_file_name, self.statuses))

        # checks that the file not found error is raised
        with self.assertRaises(FileNotFoundError):
            M.load_status_updates('fake.txt', self.statuses)

    def test_save_status_updates(self):
        '''
        Test save status updates works as expected
        '''
        good = 'save_status_test.csv'
        bad = 'bad'
        self.statuses.add_status(status_data[1][0],
                                 status_data[1][1],
                                 status_data[1][2])
        self.assertTrue(M.save_status_updates(good, self.statuses))
        self.assertTrue(os.path.exists(good))
        self.assertFalse(M.save_status_updates('bad', self.statuses))
        self.assertFalse(os.path.exists(bad))

    def test_add_user(self):
        '''
        Tests that add user calls the usercollection.add_user method correctly
        Uses a mock to avoid having to actually recall the function
        '''
        self.users.add_user = mock.Mock(return_value=True)
        test = M.add_user(test_data['Bob'][0],
                          test_data['Bob'][1],
                          test_data['Bob'][2],
                          test_data['Bob'][3],
                          self.users)
        self.assertTrue(test)
        self.users.add_user.assert_called_with(test_data['Bob'][0],
                                               test_data['Bob'][1],
                                               test_data['Bob'][2],
                                               test_data['Bob'][3])

    def test_update_user(self):
        '''
        Tests that update user calls the usercollection.modify_user
        method correctly. Uses a mock to avoid having to
        actually recall the function
        '''
        self.users.modify_user = mock.Mock(return_value=True)
        test = M.update_user(test_data['Bob'][0],
                             test_data['Bob'][1],
                             test_data['Bob'][2],
                             test_data['Bob'][3],
                             self.users)
        self.assertTrue(test)
        self.users.modify_user.assert_called_with(test_data['Bob'][0],
                                                  test_data['Bob'][1],
                                                  test_data['Bob'][2],
                                                  test_data['Bob'][3])

    def test_delete_user(self):
        '''
        Tests that delete user calls the usercollection.delete_user correctly
        '''
        self.users.delete_user = mock.Mock(return_value=True)
        test = M.delete_user(test_data['Bob'][0], self.users)
        self.assertTrue(test)
        self.users.delete_user.assert_called_with(test_data['Bob'][0])

    def test_search_user(self):
        '''
        Test that search user calls the user.search_user method correctly
        '''
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])
        test_user = self.users.database.get_by_id(test_data['Bob'][0])
        #I'm using a mock in this case but tbh don't see a lot of value from it
        self.users.search_user = mock.MagicMock(return_value=test_user)
        successful_search = M.search_user(test_user.user_id, self.users)
        self.users.search_user = mock.MagicMock(return_value=None)
        unsuccessful_search = M.search_user(test_data['Linda'][0], self.users)

        self.assertEqual(successful_search, test_user)
        self.assertEqual(unsuccessful_search, None)
        with self.assertRaises(AttributeError):
            M.search_user(test_data['Bob'][0], 'not a collection')

    def test_add_status(self):
        '''
        Tests that add status calls the instance method properly
        '''
        self.statuses.add_status = mock.Mock(return_value=True)
        test = M.add_status(status_data[1][0],
                            status_data[1][1],
                            status_data[1][2],
                            self.statuses)
        self.assertTrue(test)
        self.statuses.add_status.assert_called_with(status_data[1][0],
                                                    status_data[1][1],
                                                    status_data[1][2])

    def test_update_status(self):
        '''
        Tests that update status calls the instance method properly
        '''
        self.statuses.modify_status = mock.Mock(return_value=True)
        test = M.update_status(status_data[1][0],
                               status_data[1][1],
                               status_data[1][2],
                               self.statuses)
        self.assertTrue(test)
        self.statuses.modify_status.assert_called_with(status_data[1][0],
                                                       status_data[1][1],
                                                       status_data[1][2])

    def test_delete_status(self):
        '''
        Tests that delete user calls the usercollection.delete_user correctly
        '''
        self.statuses.delete_status = mock.Mock(return_value=True)
        test = M.delete_status(status_data[1][0], self.statuses)
        self.assertTrue(test)
        self.statuses.delete_status.assert_called_with(status_data[1][0])

    def test_search_status(self):
        '''
        Test that search status calls the search_status method correctly
        '''
        self.users.add_user(test_data['Bob'][0], test_data['Bob'][1],
                            test_data['Bob'][2], test_data['Bob'][3])
        self.statuses.add_status(status_data[1][0], status_data[1][1],
                                 status_data[1][2])
        test_status = self.statuses.database.get_by_id(status_data[1][0])

        #I'm using a mock in this case but tbh don't see a lot of value from it
        self.statuses.search_status = mock.MagicMock(return_value=test_status)
        successful_search = M.search_status(test_status.status_id,
                                            self.statuses)
        self.statuses.search_status = mock.MagicMock(return_value=None)
        unsuccessful_search = M.search_status(status_data[2][0],
                                              self.statuses)

        self.assertEqual(successful_search, test_status)
        self.assertEqual(unsuccessful_search, None)
        with self.assertRaises(AttributeError):
            M.search_status(status_data[1][0], 'not a collection')
