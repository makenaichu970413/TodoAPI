
###################################
# Module
###################################
from pymongo import MongoClient
from decouple import config
###################################


###################################
# Class
###################################
class DB:

    def __init__(self):
        username = config('USER')
        password = config('PASSWORD')
        clustername = config('CLUSTER_NAME')
        database = config('DATABASE')
        authURL = f"mongodb+srv://{username}:{password}@{clustername}.kzg50.mongodb.net/{database}?retryWrites=true&w=majority"
        # print(f"authURL: {authURL}")
        self.client = MongoClient(authURL)
        self.db = self.client[database]


    def collection(self, type):

        return self.db[type]

###################################