import ujson
from app.db import *

def get_details():
    details = get_record('admin', \
        Query().creator_id == 1)
    # Replace with session.get('user_id') for a multi-user version
    return details