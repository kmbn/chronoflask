from flask import Flask, session, redirect, url_for, render_template, flash
import ujson
from setup import *
from db import *
from chronoflask import *
from auth import *
from admin_forms import RenameChronofileForm, RenameAuthorForm


@app.route('/admin')
def admin():
    details = get_table('admin').all()
    # print('Chronofile name: %s' % (result[0]['chronofile_name']))
    # print('Chronofile author: %s' % (result[0]['author_name']))
    return render_template('admin.html', details)


@app.route('/rename_chronofile', methods=['GET', 'POST'])
def rename_chronofile():
    form = RenameChronfileForm()
    if form.validate_on_submit():
        update_record('admin', {'chronofile_name': form.new_name.data}, \
                      Query().creator_id == session.get('user_id'))
        flash('Chronfile name updated.')
        return redirect(url_for('admin'))
    return render_template('rename_chronofile.html')


@app.route('/rename_author', methods=['GET', 'POST'])
def rename_author():
    form = RenameAuthorForm()
    if form.validate_on_submit():
        update_record('admin', {'author_name': form.new_name.data}, \
                      Query().creator_id == Session.s['user_id'])
        flash('Author name updated.')
        return redirect(url_for('admin'))
    return render_template('rename_author.html')