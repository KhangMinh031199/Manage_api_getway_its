import requests
from Manage.mongo_connect import mongo_create
from Manage.Management_APIs.Controller_APIs import General_control
from fastapi import HTTPException
import datetime
from Manage import setting
import os
import logging
import traceback
mydb=mongo_create()

TOKEN_8k=''
EXPIRE_TIME_8k=0
def check_token():
    global EXPIRE_TIME_8k, TOKEN_8k
    now = datetime.datetime.now().timestamp()
    if now > EXPIRE_TIME_8k:
        url = General_control.get_link_function_service('authorization','voice_bio_v2')
        username = mydb.services.find_one({'sign':'voice_bio_v2'}).get('username')
        password = mydb.services.find_one({'sign':'voice_bio_v2'}).get('password')
        #authorization
        response = requests.post(url=url, data={'username':username, 'password':password})
        if response.status_code == 200:
            json_res = response.json()
            if json_res.get('status') == 0:
                TOKEN_8k = json_res.get('token')
                EXPIRE_TIME_8k = json_res.get('expire_time')
            else:
                return False
        else:
            return False
    return True
def delete_none(infor):
    for key,value in list(infor.items()):
        if value is None:
            del infor[key]
    return infor

def creat_update_delete_user(current_user, apifunction, name_service, gw, user_code, name=None, gender=None, date_of_birth=None, description=None, image=None):
    if check_token() is True:
        token = TOKEN_8k
        url = General_control.get_link_function_service(apifunction, name_service)
        url_gw = setting.BASE_URL + gw

        client_request = {
            'user_code': user_code,
            'name': name,
            'gender': gender,
            'description': description
        }

        files = []
        if image is not None:
            file_location = f'Manage/file/{image.filename}'
            if image.filename != '':
                client_request['image'] = image.filename
                with open(file_location, 'wb+') as file_object:
                    file_object.write(image.file.read())

                files = [
                    ('image', (image.filename, open(file_location, 'rb'), image.content_type))
                ]
            else:
                client_request['image'] = None
        else:
            client_request['image'] = None
        if date_of_birth:
            client_request['date_of_birth'] = date_of_birth.strftime('%Y/%m/%d')
        else:
            client_request['date_of_birth'] = None

        service_id = str(mydb.services.find_one({'sign': 'voice_bio_v2'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too Limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(),
                                     url, client_request, client_response, '', '', url_gw)
            return client_response
        headers = {
            'Authorization': f'Bearer {token}'
        }
        payload = delete_none(client_request)
        response = requests.post(url=url, headers=headers, files=files, data=payload)
        json_res = response.json()

        if response.status_code == 200:
            if json_res.get('status') == 0:
                General_control.decrease_remaining_request(current_user.get('_id'), service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                 General_control.getNOW(),
                                 url, client_request, json_res, client_request, json_res, url_gw)

        if image is not None:
            if (image.filename != '') and (os.path.exists(file_location)):
                files[0][1][1].close()
                os.remove(file_location)
        return json_res
    else:
        logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')