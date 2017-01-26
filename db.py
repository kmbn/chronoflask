from tinydb import TinyDB, Query
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
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
    get_table(table_name).insert(record)
    return True # Best way to phrase for debugging?


def update_record(table_name, field, query):
    get_table(table_name).update(field, query)
    return True


def get_element_id(table_name, query):
    element = get_record(table_name, query)
    element_id = element.eid
    return element_id