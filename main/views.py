from flask import Flask, session, g, redirect, url_for, render_template, \
                  flash, Blueprint
from flask_bootstrap import Bootstrap
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from db import *
from .forms import RawEntryForm

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
                tags.append(i[1:-1])
            else:
                tags.append(i[1:])
    return tags


def create_new_entry(clean_entry, timestamp, tags):
    insert_record('entries', {'entry': clean_entry, 'timestamp': timestamp, \
                    'tags': tags, 'creator_id': session.get('user_id')})
    return redirect(url_for('main.browse_all_entries'))


#@is_logged_in
@main.route('/', methods=['GET', 'POST'])
def browse_all_entries():
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    all_entries = search_records('entries', \
                                 Query().creator_id == session.get('user_id'))
    return render_template('home.html', all_entries=all_entries, form=form)


@main.route('tags/<tag>', methods=['GET', 'POST'])
def view_entries_for_tag(tag):
    '''Return entries for given tag in chronological order.'''
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_tag = search_records('entries', Query().tags.all([tag]))
    # result = get_db().search(Query().tags.all(tag))
    return render_template('tag.html', form=form, tag=tag, \
                           entries_for_tag=entries_for_tag)





def parse_input(raw_entry, current_time):
    if raw_entry == 'browse all':
        return redirect(url_for('main.browse_all_entries'))
    elif raw_entry == 'quit':
        return quit()
    elif raw_entry[:3] == 't: ':
        return view_single_entry(raw_entry[3:])
    elif raw_entry[:5] == 'tag: ':
        return view_entries_for_tag(raw_entry[5:])
    elif raw_entry[:5] == 'day: ':
        return view_entries_for_day(raw_entry[5:])
    elif raw_entry == 'register':
        register()
        return get_input()
    elif raw_entry == 'login':
        return redirect(url_for('auth.login'))
    elif raw_entry == 'logout':
        return redirect(url_for('auth.logout'))
    elif raw_entry == 'change email':
        change_email()
        return get_input()
    elif raw_entry == 'change password':
        change_password()
        return get_input()
    elif raw_entry[:14] == 'reset password':
        reset_password(raw_entry[15:])
        return get_input()
    elif raw_entry == 'about':
        return redirect(url_for('admin.get_details'))
    elif raw_entry == 'rename chrono':
        return redirect(url_for('admin.rename_chronofile'))
    elif raw_entry == 'rename author':
        return redirect(url_for('admin.rename_author'))
    else:
        return process_entry(raw_entry, current_time)


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