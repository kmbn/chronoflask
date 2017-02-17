from flask import render_template
from tinydb import Query
from app.db import get_record
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    details = get_record('admin', Query().creator_id == 1)
    return render_template('404.html', details=details), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    details = get_record('admin', Query().creator_id == 1)
    return render_template('500.html', details=details), 500