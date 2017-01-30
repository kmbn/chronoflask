import os
from flask import Flask, session, g, redirect, url_for, \
                  render_template, flash, Blueprint
from flask_bootstrap import Bootstrap
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from db import *
from .forms import RawEntryForm
from parse import *


main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def browse_all_entries():
    details = get_record('admin', Query().creator_id == 1)
    if not session.get('logged_in'):
        return render_template('welcome.html', details=details)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    results = search_records('entries', \
                             Query().creator_id == session.get('user_id'))
    all_entries = results[::-1]
    return render_template('home.html', all_entries=all_entries, form=form, \
                           details=details)


@main.route('day/<day>', methods=['GET', 'POST'])
def view_entries_for_day(day):
    '''Returns entries for given day in chronological order.'''
    if not session.get('logged_in'):
        return redirect(url_for('main.browse_all_entries'))
    details = get_record('admin', Query().creator_id == 1)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_day = search_records('entries', Query().timestamp.all([day]))
    return render_template('day.html', form=form, day=day, \
                           entries_for_day=entries_for_day, details=details)


@main.route('timestamp/<timestamp>', methods=['GET', 'POST'])
def view_single_entry(timestamp):
    '''Return a single entry based on given timestamp.'''
    if not session.get('logged_in'):
        return redirect(url_for('main.browse_all_entries'))
    details = get_record('admin', Query().creator_id == 1)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entry = get_record('entries', Query().timestamp == timestamp)
    return render_template('entry.html', form=form, timestamp=timestamp, \
                           entry=entry, details=details)


@main.route('tags')
def view_all_tags():
    if not session.get('logged_in'):
        return redirect(url_for('main.browse_all_entries'))
    details = get_record('admin', Query().creator_id == 1)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    all_entries = search_records('entries', \
                                 Query().creator_id == session.get('user_id'))
    all_tags = list()
    for entry in all_entries:
        for tag in entry['tags']:
            if tag not in all_tags:
                all_tags.append(tag)
    return render_template('tags.html', all_tags=all_tags, form=form, \
                           details=details)


@main.route('days')
def view_all_days():
    if not session.get('logged_in'):
        return redirect(url_for('main.browse_all_entries'))
    details = get_record('admin', Query().creator_id == 1)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    all_entries = search_records('entries', \
                                 Query().creator_id == session.get('user_id'))
    all_days = list()
    for entry in all_entries:
        if entry['timestamp'][:10] not in all_days:
            all_days.append(entry['timestamp'][:10])
    return render_template('days.html', all_days=all_days, form=form, \
                           details=details)


@main.route('tags/<tag>', methods=['GET', 'POST'])
def view_entries_for_tag(tag):
    '''Return entries for given tag in chronological order.'''
    if not session.get('logged_in'):
        return redirect(url_for('main.browse_all_entries'))
    details = get_record('admin', Query().creator_id == 1)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_tag = search_records('entries', Query().tags.all([tag]))
    return render_template('tag.html', form=form, tag=tag, \
                           entries_for_tag=entries_for_tag, details=details)


@main.app_errorhandler(404)
def page_not_found(e):
    details = get_record('admin', Query().creator_id == 1)
    return render_template('404.html', details=details), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    details = get_record('admin', Query().creator_id == 1)
    return render_template('500.html', details=details), 500