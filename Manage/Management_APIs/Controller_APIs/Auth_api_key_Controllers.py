from Manage.mongo_connect import mongo_create
mydb=mongo_create()

def get_user(api_key):
    return mydb.clients.find_one({'api_key': api_key})
