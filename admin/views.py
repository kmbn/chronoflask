from flask import Flask, session, redirect, url_for, render_template, flash, \
                  Blueprint
import ujson
from db import *
from .forms import RenameChronofileForm, RenameAuthorForm

admin = Blueprint('admin', __name__)


@admin.route('/')
def get_details():
    details = get_record('admin', \
                         Query().creator_id == session.get('user_id'))
    print(details)
    # print('Chronofile name: %s' % (result[0]['chronofile_name']))
    # print('Chronofile author: %s' % (result[0]['author_name']))
    return render_template('admin.html', details=details)


@admin.route('/rename_chronofile', methods=['GET', 'POST'])
def rename_chronofile():
    form = RenameChronofileForm()
    if form.validate_on_submit():
        update_record('admin', {'chronofile_name': form.new_name.data}, \
                      Query().creator_id == session.get('user_id'))
        flash('Chronfile name updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('rename_chronofile.html', form=form)


@admin.route('/rename_author', methods=['GET', 'POST'])
def rename_author():
    form = RenameAuthorForm()
    if form.validate_on_submit():
        test=update_record('admin', {'author_name': form.new_name.data}, \
                      Query().creator_id == session.get('user_id'))
        print(test)
        flash('Author name updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('rename_author.html', form=form)