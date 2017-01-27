from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required


class RawEntryForm(Form):
    raw_entry = TextAreaField('>', validators=[Required()])
    submit = SubmitField('Go')