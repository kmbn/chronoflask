import os
from flask import Flask, session, g, redirect, url_for, \
                  render_template, flash, Blueprint, current_app, abort
from flask_bootstrap import Bootstrap
from datetime import datetime
import ujson
from app.db import *
from . import main
from .forms import RawEntryForm, EditEntryForm
from app.parse import *
from app.pagination import *
from app.decorators import login_required
from app.details import get_details


@main.route('/', methods=['GET', 'POST'])
def browse_all_entries():
    '''Returns all entries (most recent entry at the top of the page).'''
    details = get_details()
    if not session.get('logged_in'):
        if details:
            register = False
        else:
            register = True
            details = {'chronofile_name': current_app.config['DEFAULT_NAME'], \
                       'author_name': current_app.config['DEFAULT_AUTHOR']}
        return render_template('welcome.html', details=details, \
                               register=register)
    form = RawEntryForm()
    # Try to validate form and create a new entry
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    # Otherwise, show the latest entries
    page = 1
    # Get entries for the given page
    entries_for_page = get_entries_for_page(page)
    # Check if there's another page, returns None if not
    next_page = check_next_page(page)
    return render_template('home.html', entries_for_page=entries_for_page, \
        form=form, details=details, next_page=next_page)


@main.route('page/<page>', methods=['GET', 'POST'])
@login_required
def view_entries_for_page(page):
    '''Returns entries for given page in reverse chronological order.'''
    try:
        int(page)
    except:
        TypeError
        return abort(404)
    page = int(page)
    if page == 1:
        return redirect(url_for('main.browse_all_entries'))
    details = get_details()
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    # Get entries for the given page
    entries_for_page = get_entries_for_page(page)
    # Check if there's another page, returns None if not
    next_page = check_next_page(page)
    prev_page = page - 1
    return render_template('page.html', form=form, \
        entries_for_page=entries_for_page, details=details, \
        page=page, next_page=next_page, prev_page=prev_page)


@main.route('day/<day>', methods=['GET', 'POST'])
@login_required
def view_entries_for_day(day):
    '''Returns entries for given day in chronological order.'''
    details = get_details()
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_day = search_records('entries', Query().timestamp.all([day]))
    if not entries_for_day:
        return abort(404)
    return render_template('day.html', form=form, day=day, \
                           entries_for_day=entries_for_day, details=details)


@main.route('timestamp/<timestamp>', methods=['GET', 'POST'])
@login_required
def view_single_entry(timestamp):
    '''Return a single entry based on given timestamp.'''
    entry = get_record('entries', Query().timestamp == timestamp)
    if not entry:
        return abort(404)
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    details = get_details()
    return render_template('entry.html', form=form, timestamp=timestamp, \
                           entry=entry, details=details)


@main.route('timestamp/<timestamp>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(timestamp):
    '''Edit an entry and return a view of the edited entry'''
    entry = get_record('entries', Query().timestamp == timestamp)
    if not entry:
        return abort(404)
    form = EditEntryForm()
    if form.validate_on_submit():
        # Split comma-delimted string of tags into a list
        # Delete spaces at the start of tags if necessary
        tags = form.new_tags.data.split(", ")
        update_record('entries', {'entry': form.new_entry.data, \
            'tags': tags}, (Query().creator_id == 1) & \
            (Query().timestamp == timestamp))
        flash('Entry updated.')
        update_pagination()
        return redirect(url_for('main.view_single_entry', timestamp=timestamp))
    form.new_entry.default = entry['entry']
    form.new_tags.default = ', '.join(entry['tags'])
    form.process()
    details = get_details()
    return render_template('edit_entry.html', form=form, timestamp=timestamp, \
        details=details)


@main.route('tags', methods=['GET', 'POST'])
@login_required
def view_all_tags():
    details = get_details()
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
    all_tags.sort()
    return render_template('tags.html', all_tags=all_tags, form=form, \
                           details=details)


@main.route('days', methods=['GET', 'POST'])
@login_required
def view_all_days():
    details = get_details()
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
@login_required
def view_entries_for_tag(tag):
    '''Return entries for given tag in chronological order.'''
    details = get_details()
    form = RawEntryForm()
    if form.validate_on_submit():
        return parse_input(form.raw_entry.data, datetime.utcnow())
    entries_for_tag = search_records('entries', Query().tags.all([tag]))
    if not entries_for_tag:
        return abort(404)
    return render_template('tag.html', form=form, tag=tag, \
                           entries_for_tag=entries_for_tag, details=details)