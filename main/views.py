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


@main.route('/', methods=['GET', 'POST'])
def browse_all_entries():
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    all_entries = search_records('entries', \
                                 Query().creator_id == session.get('user_id'))
    return render_template('home.html', all_entries=all_entries, form=form)


@main.route('day/<day>', methods=['GET', 'POST'])
def view_entries_for_day(day):
    '''Returns entries for given day in chronological order.'''
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_day = search_records('entries', Query().timestamp.all([day]))
    return render_template('day.html', form=form, day=day, \
                           entries_for_day=entries_for_day)


@main.route('timestamp/<timestamp>', methods=['GET', 'POST'])
def view_single_entry(timestamp):
    '''Return a single entry based on given timestamp.'''
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entry = get_record('entries', Query().timestamp == timestamp)
    return render_template('entry.html', form=form, timestamp=timestamp, \
                           entry=entry)


def view_all_tags():
    pass


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


def process_entry(raw_entry, current_time):
    raw_tags = find_and_process_tags(raw_entry)
    clean_entry = clean_up_entry(raw_entry, raw_tags)
    clean_tags = clean_up_tags(raw_tags)
    timestamp = create_timestamp(current_time)
    return create_new_entry(clean_entry, timestamp, clean_tags)


def clean_up_entry(raw_entry, raw_tags):
    # Strip hashtags from end of text
    bag_of_words = raw_entry.split()
    while bag_of_words[-1] in raw_tags:
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
    raw_tags = list()
    punctuation = ['.', ',']
    for i in bag_of_words:
        if i[0] == '#':
            if i[-1] in punctuation: # Clean tag if it ends w/ punctuation
                raw_tags.append(i[:-1])
            else:
                raw_tags.append(i)
    return raw_tags


def clean_up_tags(raw_tags):
    print(raw_tags)
    clean_tags = []
    for tag in raw_tags:
        clean_tags.append(tag[1:])
    return clean_tags


def create_new_entry(clean_entry, timestamp, clean_tags):
    insert_record('entries', {'entry': clean_entry, 'timestamp': timestamp, \
                    'tags': clean_tags, 'creator_id': session.get('user_id')})
    return redirect(url_for('main.browse_all_entries'))