from Manage.mongo_connect import mydb
import sys
from datetime import datetime
from bson.objectid import ObjectId

#def get_link_function_asr(apifunction):
#    asr = mydb.services.find_one({"sign": "asr"})
#    for x in asr.get("api_routing"):
#        if x.get("api_function") == apifunction:
#            return x.get('link')

# LIMIT_DURATION
def get_limit_duration(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            limit_duration = service.get('limit_duration')
            return limit_duration
    return False

# LIMIT_NUMBER_FILE


def get_remaining_number_file(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_number_file = service.get('remaining_number_file')
            return remaining_number_file
    return False

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
