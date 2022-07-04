
###################################
# Module
###################################
import os
from pymongo import MongoClient
from decouple import config
from dotenv import load_dotenv
###################################


###################################
# Class
###################################
class DB:

    def __init__(self):
        try:
            load_dotenv()
        except Exception as error:
            print(f"Production: {True}; WARNING: {error}")
        username = os.environ.get('USER')
        password = os.environ.get('PASSWORD')
        clustername = os.environ.get('CLUSTER_NAME')
        database = os.environ.get('DATABASE')
        authURL = f"mongodb+srv://{username}:{password}@{clustername}.kzg50.mongodb.net/{database}?retryWrites=true&w=majority"
        # print(f"authURL: {authURL}")
        self.client = MongoClient(authURL)
        self.db = self.client[database]


    def collection(self, type):
        return self.db[type]

###################################