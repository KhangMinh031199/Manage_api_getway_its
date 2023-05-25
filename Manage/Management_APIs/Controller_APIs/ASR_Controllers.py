from Manage.mongo_connect import mongo_create
import sys
from datetime import datetime
from bson.objectid import ObjectId
from Manage.Management_APIs.Controller_APIs import General_control
import librosa

mydb = mongo_create()

def get_limit_duration_a_file(client_id, service_id):
    info_get = "limit_duration_a_file"
    return General_control.infomation_to_get(client_id, service_id, info_get)
def get_remaining_request(client_id, service_id):
    info_get = "remaining_request"
    return General_control.infomation_to_get(client_id, service_id, info_get)
def get_remaining_duration(client_id, service_id):
    info_get = "remaining_duration"
    return General_control.infomation_to_get(client_id, service_id, info_get)

def get_duration(filename):
    try:
        lenght = librosa.get_duration(path=filename)
        return lenght
    except:
        return False

def get_remaining_number_file(client_id, service_id):
    info_get = "remaining_number_file"
    return General_control.infomation_to_get(client_id, service_id, info_get)


# LIMIT_DURATION
def get_limit_duration(client_id, service_id):
    info_get = "limit_duration"
    return General_control.infomation_to_get(client_id, service_id, info_get)

# LIMIT_NUMBER_FILE

def decrease_remaining_number_file(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_number_file = service.get('remaining_number_file')
            if remaining_number_file == -1 or remaining_number_file == 0:
                return True
            newvalue = remaining_number_file - 1
            mydb.clients.update_one({'_id': client_id, 'services.service_id': service_id},
                                    {"$set": {'services.$.remaining_number_file': newvalue}})
            return True
    return False

def decrease_duration(client_id, service_id, duration_file):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_duration = service.get('remaining_duration')
            if remaining_duration*60 >= duration_file:
                newvalue = round(remaining_duration - round(duration_file/60,2),2)
                mydb.clients.update_one({'_id': client_id, 'services.service_id': service_id},
                                        {"$set": {'services.$.remaining_duration': newvalue}})
                return True
    return False

def get_all_duration_of_customer(start_timestamp,end_timestamp,user_id):
    service = "asr"
    #get all request with method is post
    key_post = "submit_task"
    filter={
        'user_id': ObjectId(user_id),
        'service': service,
        'timestamp': {"$gte": start_timestamp, "$lte": end_timestamp},
        'link_gw': {"$regex": key_post}
    }
    results = mydb.api_logs.find(filter)
    count = 0
    all_duration = 0
    for result in results:
        if result.get('duration_file'):
            all_duration += result.get('duration_file')
        count += 1

    responses = {'number of requests': count,
                 "all_duration": round(all_duration, 2)}
    return responses
