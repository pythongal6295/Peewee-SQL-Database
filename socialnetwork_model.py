'''
Creates DB tables for the social network model
'''

import os
import peewee as pw
from loguru import logger

#pylint: disable=R0903, C0103

logger.remove()
logger.add("user_log.log", rotation="00:00", level='WARNING')

if os.path.exists('socialnetwork.db'):
    os.remove('socialnetwork.db')

db = pw.SqliteDatabase('socialnetwork.db',
                       pragmas={'foreign_keys': 1,
                                'ignore_check_constraints': 0})

class BaseModel(pw.Model):
    '''
    Base model class
    '''
    class Meta:
        '''
        Meta Class statement
        '''
        database = db

class Users(BaseModel):
    '''
    The class for the Users DB table
    '''
    user_id = pw.CharField(primary_key=True, max_length=30)
    user_name = pw.CharField(max_length=30)
    user_last_name = pw.CharField(max_length=100)
    user_email = pw.CharField(max_length=100)


    class Meta:
        '''
        Meta class statement
        '''
        database = db
        table_name = 'users'

class Status(BaseModel):
    '''
    The class for the Status DB table
    '''
    status_id = pw.CharField(primary_key=True, max_length=50)
    user_id = pw.ForeignKeyField(model=Users, backref='status',
                                 on_update='RESTRICT',
                                 on_delete='CASCADE')
    status_text = pw.CharField()

    class Meta:
        '''
        Meta class statement
        '''
        database = db
        table_name = 'status'

def create_tables(database, tables):
    '''
    Creates tables passed to the function
    '''
    database.create_tables(tables)
    return True

def main():
    '''
    Connects DB & creates tables
    '''
    db.connect(reuse_if_open=True)
    create_tables(db, (Users, Status))
    return True

if __name__ == '__main__':
    main()
