from Manage.mongo_connect import mongo_create
import json
import requests
mydb=mongo_create()

def get_authorization_facematching_v3():
    api_key = mydb.services.find_one({'sign': 'face_matching_v3'}).get('username')
    api_secret = mydb.services.find_one({'sign': 'face_matching_v3'}).get('password')

    return api_key, api_secret