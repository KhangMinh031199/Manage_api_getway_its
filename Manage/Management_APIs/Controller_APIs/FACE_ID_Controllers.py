from Manage.mongo_connect import mongo_create
from datetime import datetime
from bson.objectid import ObjectId
import sys

mydb=mongo_create()
def get_link_function_faceid(apifunction):
    faceid = mydb.services.find_one({"sign": "faceid"})
    for x in faceid.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')
