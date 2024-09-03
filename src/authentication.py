from flask import session
import bcrypt
from pymongo import MongoClient


class Auth:
    def __init__(self):
        # MongoDB setup
        self.client = MongoClient(host='18.183.148.123', port=27017, username="kamel", password="kamelpassword")
        self.db = self.client['dash_app']
        self.users_collection = self.db['users']

    def login_user(self, username, password):
        user = self.users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['logged_in'] = True
            return True
        else:
            return False

    def create_user(self, username, password):
        if self.users_collection.find_one({"username": username}):
            return "User already exists"

        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = {"username": username, "password": password}
        self.users_collection.insert_one(new_user)

        return "user created"

    def logout_user(self):
        session.pop('logged_in', None)



