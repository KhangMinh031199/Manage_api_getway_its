from Manage.mongo_connect import mongo_create
from bson.objectid import ObjectId
from datetime import datetime
import sys

mydb = mongo_create()


def get_user_id_voiceid():
    voiceid = mydb.services.find_one({'sign': 'voiceid'})
    for x in voiceid.get("api_routing"):
        if x.get("api_function") == 'user_id':
            return x.get('link')


def get_link_function_voiceid(apifunction):
    voiceid = mydb.services.find_one({"sign": "voiceid"})
    for x in voiceid.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')


def update_user_id_voiceid():
    user_id = get_user_id_voiceid()
    newvalue = str(int(user_id) + 1)
    mydb.services.update_one({'sign': 'voiceid', 'api_routing.api_function': 'user_id'},
                             {"$set": {'api_routing.$.link': newvalue}})


def check_index_elastic(log):
    dic = {}
    try:
        dic["id"] = str(log.get('_id'))
        if log.get('user_id') and log.get('user_id') != "":
            dic["user_id"] = str(log.get('user_id'))
        else:
            dic["user_id"] = 'None'

        if log.get('username') and log.get('username') != "":
            dic["username"] = log.get('username')
        else:
            dic["username"] = 'None'

        if log.get('service') and log.get('service') != "":
            dic["service"] = log.get('service')
        else:
            dic["service"] = 'None'

        if log.get('timestamp'):
            dic["timestamp"] = log.get('timestamp')
        else:
            dic["timestamp"] = 'None'

        if log.get('link_api'):
            dic["link_api"] = log.get('link_api')
        else:
            dic["link_api"] = 'None'

        if log.get('link_gw'):
            dic["link_gw"] = log.get('link_gw')
        else:
            dic["link_gw"] = 'None'
        # ----
        if log.get('request') and log.get('request') != None:
            if type(log.get('request')) == dict:
                dic["request"] = json.dumps(
                    json_util.dumps(log.get('request')))
            else:
                dic["request"] = log.get('request')
        else:
            dic["request"] = 'None'

        # ----
        if log.get('response') and log.get('response') != None:
            if type(log.get('response')) == dict:
                dic["response"] = json.dumps(
                    json_util.dumps(log.get('response')))
            else:
                dic["response"] = log.get('response')
        else:
            dic["response"] = "None"
        # ----
        if log.get('origin_request') and log.get('origin_request') != None:
            if type(log.get('origin_request')) == dict:
                dic["origin_request"] = json.dumps(
                    json_util.dumps(log.get('origin_request')))
            else:
                dic["origin_request"] = log.get('origin_request')
        else:
            dic["origin_request"] = 'None'
        # ----
        if log.get('origin_response') and log.get('origin_response') != None:
            if type(log.get('origin_response')) == dict:
                dic["origin_response"] = json.dumps(
                    json_util.dumps(log.get('origin_response')))
            else:
                dic["origin_response"] = log.get('origin_response')
        else:
            dic["origin_response"] = 'None'
    except:
        pass

    try:
        index_api_logs_item_orther(dic)
    except:
        pass
