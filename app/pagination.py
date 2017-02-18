from flask import redirect, url_for, session, abort
import ujson
from app.db import *


def update_pagination():
    ''' Creates a table of entries organized by page
    for use when browsing entries. '''
    results = search_records('entries', \
        Query().creator_id == session.get('user_id'))
    all_entries = results[::-1]
    limit = len(all_entries)
    total = 0 # counter for total number of entries processed
    count = 0 # counter for number of entries—loop at 10
    page = 1 # will be key for dictionary of pages
    p_entries = list()
    get_table('pagination').purge() # clear the old pagination table
    for entry in all_entries:
        total += 1
        count += 1
        p_entries.append(entry)
        if count == 10 or total == limit:
            insert_record('pagination', {'page': page, 'entries': p_entries})
            del p_entries[:] # start the list fresh
            page += 1
            count = 0
    return True


# Get entries for the given page
def get_entries_for_page(page):
    results = get_record('pagination', Query().page == page)
    if not results:
        return abort(404)
    else:
        return results['entries']

def check_next_page(page):
    next_page = page + 1
    if not get_record('pagination', Query().page == next_page):
        return None
    else:
        return next_page