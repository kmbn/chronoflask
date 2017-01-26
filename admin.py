from mocksession import Session
from db import *
from auth import *

@is_logged_in
def get_chronofile_details():
    result = get_table('admin').all()
    print('Chronofile name: %s' % (result[0]['chronofile_name']))
    print('Chronofile author: %s' % (result[0]['author_name']))
    return True


@is_logged_in
def rename_chronofile():
    new_name = input('Enter new name for chronofile: ')
    update_record('admin', {'chronofile_name': new_name}, \
                  Query().creator_id == Session.s['user_id'])
    return True


@is_logged_in
def rename_author():
    new_name = input('Enter new author name: ')
    update_record('admin', {'author_name': new_name}, \
                  Query().creator_id == Session.s['user_id'])
    return True