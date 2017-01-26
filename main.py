from flask import Flask, session, g, redirect, url_for, render_template, flash, \
                  Blueprint
from flask_bootstrap import Bootstrap
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from setup import *
from db import *

main = Blueprint('main', __name__)


def process_entry(raw_entry, current_time):
    tags = find_and_process_tags(raw_entry)
    clean_entry = clean_up_entry(raw_entry, tags)
    timestamp = create_timestamp(current_time)
    return create_new_entry(clean_entry, timestamp, tags)


def clean_up_entry(raw_entry, tags):
    # Strip hashtags from end of text
    bag_of_words = raw_entry.split()
    while bag_of_words[-1] in tags:
        bag_of_words.pop()
    stripped_entry = ' '.join(bag_of_words)
    # Uppercase first letter
    clean_entry = stripped_entry[0].upper() + stripped_entry[1:]
    return clean_entry


def create_timestamp(current_time):
    #Convert datetime object to string for use with JSON.
    #May not be necessary with alterate storage or extensions.
    timestamp = datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S')
    return timestamp


def find_and_process_tags(raw_entry):
    '''
    Extract all hashtags from the entry.
    '''
    bag_of_words = raw_entry.split()
    tags = []
    punctuation = ['.', ',']
    for i in bag_of_words:
        if i[0] == '#':
            if i[-1] in punctuation: # Clean tag if it ends w/ punctuation
                tags.append(i[:-1])
            else:
                tags.append(i)
    return tags


def create_new_entry(clean_entry, timestamp, tags):
    insert_record('entries', {'entry': clean_entry, 'timestamp': timestamp, \
                    'tags': tags})
    return get_input()


#@is_logged_in
@main.route('/')
def browse_all_entries():
    all_entries = get_table('entries').all()
    return render_template('home.html', all_entries=all_entries)


def view_single_entry(timestamp):
    '''
    Return a single entry based on given timestamp
    '''
    result = get_record('entries', Query().timestamp == timestamp)
    if not result:
        print('No entry for that timestamp.')
    else:
        print('Entry for %s:' % (result['timestamp']))
        print('%s: %s :: filed under %s' % (result['timestamp'], \
              result['entry'], result['tags']))
    return get_input()



def view_entries_for_tag(tag):
    '''
    Return entries for given tag in chronological order.
    '''
    result = search_records('entries', Query().tags.all([tag]))
    # result = get_db().search(Query().tags.all(tag))
    if not result:
        print('No entries for that tag.')
    else:
        print('Entries for tag %s:' % (tag))
        for i in result:
            print('%s: %s :: filed under %s' % (i['timestamp'], \
                  i['entry'], i['tags']))
    return get_input()



def view_entries_for_day(day):
    '''
    Returns entries for given day in chronological order.
    '''
    result = search_records('entries', Query().timestamp.all([day]))
    if not result:
        print('No entries for that day.')
    else:
        for i in result:
            print('%s: %s :: filed under %s' % (i['timestamp'], \
                  i['entry'], i['tags']))
    return get_input()