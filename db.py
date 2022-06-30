
###################################
# Module
###################################
from pymongo import MongoClient
###################################


###################################
# Class
###################################
class DB:

    def __init__(self):
        username = "makenaichu970413"
        password = "Chu970413045109"
        clustername = "cluster0"
        database = "todo"
        authURL = f"mongodb+srv://{username}:{password}@{clustername}.kzg50.mongodb.net/{database}?retryWrites=true&w=majority"
        self.client = MongoClient(authURL)
        self.db = self.client[database]

    def collection(self, type):

        return self.db[type]

###################################