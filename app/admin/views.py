from flask import Flask, session, redirect, url_for, render_template, flash, \
                  Blueprint
import ujson
from app.db import *
from . import admin
from .forms import RenameChronofileForm, RenameAuthorForm
from app.decorators import login_required


@admin.route('/')
@login_required
def get_details():
    '''Display name of site, author, etc. as well as links to edit
    those details and change email, password, etc.'''
    details = get_record('admin', \
                         Query().creator_id == session.get('user_id'))
    return render_template('admin.html', details=details)


@admin.route('/rename_chronofile', methods=['GET', 'POST'])
@login_required
def rename_chronofile():
    details = get_record('admin', Query().creator_id == 1)
    form = RenameChronofileForm()
    if form.validate_on_submit():
        update_record('admin', {'chronofile_name': form.new_name.data}, \
                      Query().creator_id == session.get('user_id'))
        flash('Chronfile name updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('rename_chronofile.html', \
                           form=form, details=details)


@admin.route('/rename_author', methods=['GET', 'POST'])
@login_required
def rename_author():
    details = get_record('admin', Query().creator_id == 1)
    form = RenameAuthorForm()
    if form.validate_on_submit():
        test=update_record('admin', {'author_name': form.new_name.data}, \
                           Query().creator_id == session.get('user_id'))
        flash('Author name updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('rename_author.html', form=form, details=details)
