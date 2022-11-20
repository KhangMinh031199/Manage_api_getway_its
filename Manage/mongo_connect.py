from pymongo import MongoClient
from Manage import setting
from collections import OrderedDict
import sys


#def mongo_create():
#    if 'cmc' in sys.argv:
#        mongodb = MongoClient(

#            setting.MONGODB_HOST_CMC,
#            setting.MONGODB_PORT,
#            # document_class=OrderedDict,
#            maxPoolSize=200,
#            serverSelectionTimeoutMS=90000)

#       mydb = mongodb[setting.MONGODB_NAME]
#       mydb.authenticate(setting.MONGODB_USER_CMC,
#                         setting.MONGODB_PASSWORD_CMC)
#   else:
#       mongodb = MongoClient(
#           setting.MONGODB_HOST,
#           setting.MONGODB_PORT,
            # document_class=OrderedDict,
#            maxPoolSize=200,
#            serverSelectionTimeoutMS=90000)

#        mydb = mongodb[setting.MONGODB_NAME]
#        if 'local' not in sys.argv:
#            mydb.authenticate(setting.MONGODB_USER, setting.MONGODB_PASSWORD)
#    return mydb

def mongo_create():
    mongodb = MongoClient(
        setting.MONGODB_HOST,
        setting.MONGODB_PORT,
        # document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

    mydb = mongodb[setting.MONGODB_NAME]
    #if 'local' not in sys.argv:
    mydb.authenticate(setting.MONGODB_USER, setting.MONGODB_PASSWORD)
        #mydb = "mongodb+srv://khangminh123:1234567890p@localhost:27017/api_getway?retryWrites=true&w=majority"
    return mydb

mydb= mongo_create()