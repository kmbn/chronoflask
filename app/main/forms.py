from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class RawEntryForm(Form):
    raw_entry = StringField('New entry in log:', validators=[Required()])
    submit = SubmitField('Post entry')