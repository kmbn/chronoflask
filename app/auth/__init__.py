from flask import Blueprint
from passlib.context import CryptContext

auth = Blueprint('auth', __name__)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])

from . import views