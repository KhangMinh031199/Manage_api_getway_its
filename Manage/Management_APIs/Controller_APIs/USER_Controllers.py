from bson.objectid import ObjectId
from Manage.mongo_connect import mydb
from datetime import datetime
import re


def get_service_info(service_id):
    if not isinstance(service_id, ObjectId):
        service_id = ObjectId(service_id)

    return mydb.services.find_one({'_id': service_id})

def get_services():
    find = mydb.services.find()
    if find is None:
        return []
    services = []
    for x in find:
        service = {}
        service['_id'] = str(x.get('_id'))
        service['name'] = x.get('name')
        if x.get('description') is not None:
            service['description'] = x.get('description')
        services.append(service)
    return services


# lấy thông tin chi tiết dịch vụ đã đăng ký thông qua client id
def get_service_registered(client_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    find_client = mydb.clients.find_one({"_id": client_id})
    if find_client is None:
        return []
    register_services = find_client.get('services')
    services = []
    for x in register_services:
        service = (get_service_info(x['service_id']))
        if service is None:
            continue
        service['register_date'] = x["register_date"]
        service['limit_request'] = x['limit_request']
        service['remaining_request'] = x['remaining_request']
        services.append(service)
    return services

def check_password(pw):
    regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$"
    pat = re.compile(regex)
    mat = re.search(pat, pw)
    if mat:
        return True
    return False


