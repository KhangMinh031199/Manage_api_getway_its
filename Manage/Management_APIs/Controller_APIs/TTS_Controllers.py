from Manage.mongo_connect import mongo_create
from bson.objectid import ObjectId
from Manage.Management_APIs.Controller_APIs import General_control
from Manage import setting
import requests
import logging
import traceback
from fastapi import HTTPException

mydb = mongo_create()
def get_link_function_tts(apifunction):
    tts = mydb.services.find_one({"sign": "tts"})
    for x in tts.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

# LIMIT_CHARACTER
def get_remaining_character(client_id, service_id):
    info_get = "remaining_character"
    return General_control.infomation_to_get(client_id, service_id, info_get)

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


# Xử lý Audio URL, Audio URL 8k,Submit Task. Vì tiền xử lý của các api này giống nhau
# Nên viết chung 1 hàm xử lý để gọi
def processing(text, voiceId, current_user, apifunction, name_service, subdirectory, msg_error, volumn = None, speed = None):
    try:
        url = General_control.get_link_function_service(apifunction, name_service)
        url_gw = setting.BASE_URL + subdirectory
        length = len(text)

        client_request = {
            'text': text,
            'voiceId': voiceId,
            'length': length,
            'volumn': volumn,
            'speed': speed,
        }

        if volumn:
            if volumn < 0.2 or volumn > 5:
                client_response = {
                    'status_code': 0,
                    'msg': 'Giá trị volumn trong khoảng từ 0.2 đến 5'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
                return client_response

        if speed:
            if speed < 0.8 or speed > 1.2:
                client_response = {
                    'status_code': 0,
                    'msg': 'Giá trị speed trong khoảng từ 0.8 đến 1.2'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
                return client_response

        service_id = str(mydb.services.find_one({'sign': 'tts'}).get('_id'))
        limit_request = General_control.get_remaining_request(current_user.get('_id'), service_id)
        remaining_character = get_remaining_character(current_user.get('_id'), service_id)
        token = mydb.services.find_one({'sign': 'tts'}).get('password')
        if limit_request == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        payload = {
            'token': token,
            'text': text,
            'voiceId': voiceId,
            'volumn': volumn,
            'speed': speed,
        }
        files = []
        headers = {}

        if remaining_character == -1:
            response = requests.post(url=url, headers=headers, data=payload, files=files)
            res = response.json()
            if res.get('status') == 0:
                General_control.decrease_remaining_request(current_user.get('_id'), service_id)
                decrease_remaining_character(current_user.get('_id'), service_id, length)

            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                     General_control.getNOW(), url, client_request, res, payload, res, url_gw)

            return res
        if remaining_character < length:
            client_response = {
                'status_code': 105,
                'msg': f"Bạn không đủ số ký tự để sử dụng. Số ký tự còn lại: {remaining_character}"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        response = requests.post(url=url, headers=headers, data=payload, files=files)
        res_json = response.json()
        if res_json.get('status') == 0 or res_json.get('status') == 100:
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            decrease_remaining_character(current_user.get('_id'), service_id, length)

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                 General_control.getNOW(), url, client_request, res_json, payload, res_json, url_gw)

        return res_json
    except:
        logging.info("TTS Service ERROR! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail=msg_error)

def statistics(start_timestamp, end_timestamp, user_id):
    name_service = 'tts'
    #get all request with method is post
    key_post = 'path|submit'
    filter={
        'service': name_service,
        'timestamp': {'$gte': start_timestamp, '$lte': end_timestamp},
        'user_id': ObjectId(user_id),
        'link_gw': {'$regex': key_post}
    }
    results = mydb.api_logs.find(filter)
    sum_length = 0
    sum_num_word = 0
    total_request = 0
    for result in results:
        info_length = result.get('request')
        info_sum_words = (result.get('response')).get('stats')
        if info_sum_words:
            sum_length += info_length.get('length')
            sum_num_word += info_sum_words.get('num_words')
            total_request += 1

    response = {
        'Total request': total_request,
        'Total length': sum_length,
        'Total word': sum_num_word
    }
    return response
