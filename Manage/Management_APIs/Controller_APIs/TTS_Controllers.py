from Manage.mongo_connect import mydb
from bson.objectid import ObjectId

def get_link_function_tts(apifunction):
    tts = mydb.services.find_one({"sign": "tts"})
    for x in tts.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

# LIMIT_CHARACTER
def get_remaining_character(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_character = service.get('remaining_character')
            return remaining_character
    return False


def decrease_remaining_character(client_id, service_id, number):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_character = service.get('remaining_character')
            if remaining_character == -1 or remaining_character == 0:
                return True
            newvalue = remaining_character - number
            mydb.clients.update_one({'_id': client_id, 'services.service_id': service_id},
                                    {"$set": {'services.$.remaining_character': newvalue}})
            return True
    return False

