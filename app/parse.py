from flask import redirect, url_for, session
from datetime import datetime
from db import insert_record

def parse_input(raw_entry, current_time):
    if raw_entry == 'browse all':
        return redirect(url_for('main.browse_all_entries'))
    elif raw_entry == 'quit':
        return quit()
    elif raw_entry[:3] == 't: ':
        return redirect(url_for('main.view_single_entry', timestamp=raw_entry[3:]))
    elif raw_entry[:5] == 'tag: ':
        return redirect(url_for('main.view_entries_for_tag', tag=raw_entry[5:]))
    elif raw_entry[:5] == 'day: ':
        return redirect(url_for('view_entries_for_day', day=raw_entry[5:]))
    elif raw_entry == 'login':
        return redirect(url_for('auth.login'))
    elif raw_entry == 'logout':
        return redirect(url_for('auth.logout'))
    elif raw_entry == 'change email':
        change_email()
        return get_input()
    elif raw_entry == 'change password':
        change_password()
        return get_input()
    elif raw_entry[:14] == 'reset password':
        reset_password(raw_entry[15:])
        return get_input()
    elif raw_entry == 'about':
        return redirect(url_for('admin.get_details'))
    elif raw_entry == 'rename chrono':
        return redirect(url_for('admin.rename_chronofile'))
    elif raw_entry == 'rename author':
        return redirect(url_for('admin.rename_author'))
    else:
        return process_entry(raw_entry, current_time)


def process_entry(raw_entry, current_time):
    raw_tags = find_and_process_tags(raw_entry)
    clean_entry = clean_up_entry(raw_entry, raw_tags)
    clean_tags = clean_up_tags(raw_tags)
    timestamp = create_timestamp(current_time)
    return create_new_entry(clean_entry, timestamp, clean_tags)


def clean_up_entry(raw_entry, raw_tags):
    # Strip hashtags from end of text
    bag_of_words = raw_entry.split()
    if bag_of_words == raw_tags:
        clean_entry = bag_of_words[0]
    else:
        while bag_of_words[-1] in raw_tags:
            bag_of_words.pop()
        stripped_entry = ' '.join(bag_of_words)
        # Uppercase first letter
        clean_entry = stripped_entry[0].upper() + stripped_entry[1:]
    return clean_entry


def create_timestamp(current_time):
    timestamp = datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S')
    return timestamp


def find_and_process_tags(raw_entry):
    '''
    Extract all hashtags from the entry.
    '''
    bag_of_words = raw_entry.split()
    raw_tags = list()
    punctuation = ['.', ',']
    for i in bag_of_words:
        if i[0] == '#':
            if i[-1] in punctuation: # Clean tag if it ends w/ punctuation
                raw_tags.append(i[:-1])
            else:
                raw_tags.append(i)
    return raw_tags


def clean_up_tags(raw_tags):
    print(raw_tags)
    clean_tags = []
    for tag in raw_tags:
        clean_tags.append(tag[1:])
    return clean_tags


def create_new_entry(clean_entry, timestamp, clean_tags):
    insert_record('entries', {'entry': clean_entry, 'timestamp': timestamp, \
                    'tags': clean_tags, 'creator_id': session.get('user_id')})
    return redirect(url_for('main.browse_all_entries'))