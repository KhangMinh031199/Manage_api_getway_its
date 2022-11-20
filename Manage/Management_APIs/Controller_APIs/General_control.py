from datetime import datetime
import sys
from bson.objectid import ObjectId
from Manage.mongo_connect import mydb

def getNOW():
    return datetime.now().timestamp()

def get_link_function_service(apifunction, name_service):
    service = mydb.services.find_one({"sign": name_service})
    for x in service.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

def save_log(user_id, username, service, timestamp, link_api, request, response, origin_request, origin_response, link_gw=None):
    insert_data = {"user_id": user_id,
                   "username": username,
                   "service": service,
                   "timestamp": timestamp,
                   "link_api": link_api,
                   "link_gw": link_gw,
                   "request": request,
                   "response": response,
                   "origin_request": origin_request,
                   "origin_response": origin_response
                   }
    log_id = mydb.api_logs.insert_one(insert_data)
    insert_data['id'] = str(log_id.inserted_id)
    if 'cmc' not in sys.argv:
        try:
            check_index_elastic(insert_data)
        except:
            pass
    return True

# Lấy ra số request còn lại của khách hàng của 1 dịch vụ
def get_remaining_request(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_request = service.get('remaining_request')
            return remaining_request
    return False

# Giảm số request xuống đi 1
def decrease_remaining_request(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_request = service.get('remaining_request')
            if remaining_request == -1:
                return True
            newvalue = remaining_request - 1
            mydb.clients.update_one({'_id': client_id, 'services.service_id': service_id},
                                    {"$set": {'services.$.remaining_request': newvalue}})
            return True
    return False

####
def check_have_asr(client_id):
    id_asr = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))
    is_asr = mydb.clients.find_one(
        {'_id': ObjectId(client_id), 'services.service_id': id_asr})
    if is_asr is None:
        return False
    return True

def get_url_webhook(client_id):
    url = mydb.clients.find_one(
        {'_id': ObjectId(client_id)}).get('url_webhook')
    if url is None:
        return ""
    return url


