from datetime import datetime
import sys
from bson.objectid import ObjectId
from Manage.mongo_connect import mongo_create
import json
from bson import json_util
from elasticsearch import Elasticsearch
from Manage import setting
es = Elasticsearch([setting.ELASTICSEARCH_SERVER],
                   http_auth=(setting.ELASTICSEARCH_USER,
                              setting.ELASTICSEARCH_PASSWORD),
                   scheme="http",
                   port=9200,
                   timeout=3000,
                   max_retries=10,
                   retry_on_timeout=True)

mydb=mongo_create()
def getNOW():
    return datetime.now().timestamp()

def get_link_function_service(apifunction, name_service):
    service = mydb.services.find_one({"sign": name_service})
    for x in service.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')


def get_elastic(index_name, index_id):
    try:
        res = es.get(index=index_name, id=str(index_id))
        return res
    except:
        return ''

def remove_elastic(index_name, index_id):
    res = es.delete(index=index_name, id=str(index_id))
    es.indices.refresh(index=index_name)
    return res

def index_elastic(index_name, index_id, data):
    res = es.index(index=index_name,
                   doc_type=index_name,
                   id=str(index_id),
                   body=data)

    es.indices.refresh(index=index_name)
    return res


def index_api_logs_item_orther(log):
    info = {}
    info['id'] = str(log.get("id"))
    info['user_id'] = log.get("user_id")
    info['service'] = log.get('service')
    info['timestamp'] = log.get('timestamp')
    info['link_api'] = log.get('link_api')
    info['link_gw'] = log.get('link_gw')
    info['request'] = log.get('request')
    info['response'] = log.get('response')
    info['origin_request'] = log.get('origin_request')
    info['origin_response'] = log.get('origin_response')
    # print(info)
    check_api_logs_index = get_elastic('api_logs_other', info['id'])
    if check_api_logs_index and len(check_api_logs_index) > 0:
        remove_elastic('api_logs_other', info['id'])
        index_elastic('api_logs_other', info['id'], info)
    else:
        index_elastic('api_logs_other', info['id'], info)


def check_index_elastic(log):
    dic = {}
    try:
        dic["id"] = str(log.get('_id'))
        #print(dic.get('id'))
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


def save_log(user_id, username, service, timestamp, link_api, request, response, origin_request, origin_response, link_gw=None, duration_file = None):
    insert_data = {"user_id": user_id,
                   "username": username,
                   "service": service,
                   "timestamp": timestamp,
                   "link_api": link_api,
                   "link_gw": link_gw,
                   "request": request,
                   "response": response,
                   "origin_request": origin_request,
                   "origin_response": origin_response,
                   "duration_file": duration_file
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

#information_to_get: Đây là hàm chung, tái sử dụng nhiều lần để lấy thông tin cần lấy trong Mongodb
def infomation_to_get(client_id, service_id, info_get):
    #client_id: ID của khách hàng sử dụng dịch vụ
    #sevice_id: ID của dịch vụ
    #info_get: Thông tin cần lấy của dịch vụ mà khách hàng đăng ký như: Giới hạn request còn lại
    #giới hạn ký tự còn lai, giới hạn thời lượng còn lại ...
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_request = service.get(info_get)
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


