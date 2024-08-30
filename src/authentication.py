from flask import session, redirect, url_for
import bcrypt
from pymongo import MongoClient


class Auth:
    def __init__(self):
        # MongoDB setup
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['dash_app']
        self.users_collection = self.db['users']

    def login_user(self, username, password):
        user = self.users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['logged_in'] = True
            return True
        else:
            return False

    def logout_user(self):
        session.pop('logged_in', None)
