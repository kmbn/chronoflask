from tinydb import TinyDB, Query
import ujson


def get_db():
    db = TinyDB('db.json')
    return db


def get_table(table_name):
    table = get_db().table(table_name)
    return table


def get_record(table_name, query):
    result = get_table(table_name).get(query)
    return result


def search_records(table_name, query):
    results = get_table(table_name).search(query)
    return results


def insert_record(table_name, record):
    # Inserting a record returns the element id of the new record.
    element_id = get_table(table_name).insert(record)
    return element_id


def update_record(table_name, field, query):
    get_table(table_name).update(field, query)
    return True


def get_element_id(table_name, query):
    element = get_record(table_name, query)
    element_id = element.eid
    return element_id