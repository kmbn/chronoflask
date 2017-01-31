from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class RenameChronofileForm(Form):
    new_name = StringField('Enter new name for chronofile:', \
                           validators=[Required()])
    submit = SubmitField('Rename chronofile')


class RenameAuthorForm(Form):
    new_name = StringField('Enter new author name:', \
                           validators=[Required()])
    submit = SubmitField('Rename author')