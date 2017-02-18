from flask import render_template
from tinydb import Query
from app.db import get_record
from . import main
from app.details import get_details

@main.app_errorhandler(404)
def page_not_found(e):
    details = get_details()
    return render_template('404.html', details=details), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    details = get_details()
    return render_template('500.html', details=details), 500