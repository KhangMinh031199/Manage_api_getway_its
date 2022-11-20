from Manage.mongo_connect import mydb
from Manage.Management_APIs.Controller_APIs import General_control

TIME_RENEW_DATABASE = 2592000  # 1 month

def get_link_function_identification(apifunction):
    identification = mydb.services.find_one({"sign": "identification"})
    for x in identification.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

def validation_check_identification_id(id):
    if len(id) == 9 or len(id) == 12:
        return True
    return False

def check_identification_in_db(user_id, name_service, request):
    service_is_exist = mydb.user_identification.find_one(
        {"user_id": user_id, "services.name_service": name_service, "services.request": request})
    if service_is_exist:
        find_service = None
        for service in service_is_exist.get('services'):
            if service.get('name_service') == name_service and service.get('request') == request:
                find_service = service
                break
        if find_service is None:
            # user_identification_push_service(user_id, name_service, request, response)
            return "push_service"
        if TIME_RENEW_DATABASE < (General_control.getNOW() - find_service.get('last_update')):
            # user_identification_update_service(user_id, name_service, request, response)
            return "update"
        return find_service
    else:
        user_is_exist = mydb.user_identification.find_one({'user_id': user_id})
        if not user_is_exist:
            # user_identification_create_user(user_id, name_service, request, response)
            return 'create_user'
        else:
            # user_identification_push_service(user_id, name_service, request, response)
            return 'push_service'

def user_identification_create_user(user_id, name_service, request, response):
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
    insert = mydb.user_identification.insert_one(insert_data)
    if insert is None:
        return False
    return True

def user_identification_push_service(user_id, name_service, request, response):
    insert_data = {
        "name_service": name_service,
        "request": request,
        "response": response,
        "last_update": General_control.getNOW()
    }
    addToSet = mydb.user_identification.update_one(
        {"user_id": user_id},
        {'$addToSet': {
            "services": insert_data
                    }
        }
    )
    if addToSet is None:
        return False
    return True

def user_identification_update_service(user_id, name_service, request, response):
    insert_data = {
        "name_service": name_service,
        "request": request,
        "response": response,
        "last_update": General_control.getNOW()
    }
    set = mydb.user_identification.find_one_and_update(
        {"user_id": user_id, "services.name_service": name_service},
        {'$set': {
            "services.$": insert_data
        }
        }
    )
    if set is None:
        return False
    return True