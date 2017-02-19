import re
from flask import Markup
from flask_wtf import Form
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required


class RawEntryForm(Form):
    raw_entry = StringField('New entry in chronofile:', validators=[Required()])
    submit = SubmitField('Post entry')


# Custom validators

def no_hashtags(form, field):
    if bool(re.search(r'#', field.data)):
        raise ValidationError(Markup("Don't start tags with \
            <code>#</code> here."))

def use_commas(form, field):
    tags = field.data.split(' ')
    items = len(tags)
    print(items)
    if items != 1:
        count = 1
        for i in tags:
            print(i)
            print(i[-1])
            if i[-1] == ',':
                print(i[-1])
                count += 1
        print(count)
        if count < items:
            raise ValidationError(Markup('Separate tags \
                with commas like this: <code>tag1, tag2</code>.'))


class EditEntryForm(Form):
    new_entry = StringField('Edit entry text:', validators=[Required()])
    new_tags = StringField("Edit tags: (separate with commas, don't use #)", \
        validators=[no_hashtags, use_commas])
    submit = SubmitField('Save edited entry')