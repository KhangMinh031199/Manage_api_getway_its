from Manage.mongo_connect import mongo_create
import hashlib
import re
from Manage.Management_APIs.Controller_APIs import General_control
from datetime import datetime

mydb=mongo_create()
TIME_RENEW_DATABASE = 2592000  # 1 month

def get_request_id_lookup():
    lookup = mydb.services.find_one({'sign': 'lookup'})
    for x in lookup.get("api_routing"):
        if x.get("api_function") == 'request_id':
            return x.get('link')

def get_secret_token(client_id, secret_key, request_id, msisdn):
    mystring = f'\\u0000{client_id}\\u0000{secret_key}\\u0000{request_id}\\u0000{msisdn}\\u0000'
    return hashlib.sha256(mystring.encode()).hexdigest()

def get_secret_token_vs2(client_id,secret_key,request_id,msisdn,n,cp1,cp2,cp3):
    mystring=f'\\u0000{client_id}\\u0000{secret_key}\\u0000{request_id}\\u0000{msisdn}\\u0000{n}\\u0000{cp1}\\u0000{cp2}\\u0000{cp3}\\u0000'
    return hashlib.sha256(mystring.encode()).hexdigest()

def get_secret_token_vs3(client_id,secret_key,request_id,msisdn,accuracy_of_address,n):
    mystring=f'\\u0000{client_id}\\u0000{secret_key}\\u0000{request_id}\\u0000{msisdn}\\u0000{accuracy_of_address}\\u0000{n}\\u0000'
    return hashlib.sha256(mystring.encode()).hexdigest()

def get_secret_token_vs4(client_id,secret_key,request_id,nic_no):
    mystring=f'\\u0000{client_id}\\u0000{secret_key}\\u0000{request_id}\\u0000{nic_no}\\u0000'
    return hashlib.sha256(mystring.encode()).hexdigest()



def validation_check_lookup_phone(phone):
    if len(phone) != 11:
        return False
    reg = "(84[3|5|7|8|9])+([0-9]{8})\\b"
    pat = re.compile(reg)
    mat = re.search(pat, phone)
    if mat:
        return True
    else:
        return False

###
def check_in_db(user_id, name_service, request):
    service_is_exist = mydb.user_lookup.find_one(
        {"user_id": user_id, "services.name_service": name_service, "services.request": request})
    if service_is_exist:
        find_service = None
        for service in service_is_exist.get('services'):
            if service.get('name_service') == name_service and service.get('request') == request:
                find_service = service
                break
        if find_service is None:
            # user_lookup_push_service(user_id, name_service, request, response)
            return "push_service"
        if TIME_RENEW_DATABASE < General_control.getNOW() - find_service.get('last_update'):
            # user_lookup_update_service(user_id, name_service, request, response)
            return "update"
        return find_service
    else:
        user_is_exist = mydb.user_lookup.find_one({'user_id': user_id})
        if not user_is_exist:
            # user_lookup_create_user(user_id, name_service, request, response)
            return 'create_user'
        else:
            # user_lookup_push_service(user_id, name_service, request, response)
            return 'push_service'


###
def user_lookup_update_service(user_id, name_service, request, response):
    insert_data = {
        "name_service": name_service,
        "request": request,
        "response": response,
        "last_update": General_control.getNOW()
    }
    set = mydb.user_lookup.find_one_and_update(
        {"user_id": user_id, "services.name_service": name_service},
        {'$set': {
            "services.$": insert_data
        }
        }
    )
    if set is None:
        return False
    return True

def user_lookup_push_service(user_id, name_service, request, response):
    insert_data = {
        "name_service": name_service,
        "request": request,
        "response": response,
        "last_update": General_control.getNOW()
    }
    addToSet = mydb.user_lookup.update_one(
        {"user_id": user_id},
        {'$addToSet': {
            "services": insert_data
        }
        }
    )
    if addToSet is None:
        return False
    return True

def user_lookup_create_user(user_id, name_service, request, response):
    insert_data = {
        "user_id": user_id,
        "services": [
            {"name_service": name_service,
             "request": request,
             "response": response,
             "last_update": General_control.getNOW()
             }
        ]
    }
    insert = mydb.user_lookup.insert_one(insert_data)
    if insert is None:
        return False
    return True


def update_request_id_lookup():
    request_id = get_request_id_lookup()
    if request_id == "1000000000":
        request_id = "0"
    newvalue = str(int(request_id) + 1)
    mydb.services.update_one({'sign': 'lookup', 'api_routing.api_function': 'request_id'},
                             {"$set": {'api_routing.$.link': newvalue}})