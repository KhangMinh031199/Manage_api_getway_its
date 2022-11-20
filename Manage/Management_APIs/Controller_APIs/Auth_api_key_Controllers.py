from Manage.mongo_connect import mydb

def get_user(api_key):
    return mydb.clients.find_one({'api_key': api_key})
