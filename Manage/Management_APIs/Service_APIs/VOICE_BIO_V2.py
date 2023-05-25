import datetime
from Manage import setting
from Manage.Management_APIs.Controller_APIs import VOICE_BIO_V2_Controllers, General_control
from fastapi import HTTPException, APIRouter, Depends, Form, UploadFile, File
from typing import Union
from fastapi_limiter.depends import RateLimiter
from Manage.mongo_connect import mongo_create
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Schemas.Schemas_share import User
import logging
import traceback
import requests
import os

mydb = mongo_create()
VOICE_BIO_V2 = APIRouter(tags=['VOICE BIO V2'])

@VOICE_BIO_V2.post('/api/voicebio/v2/user/create', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_create_user(user_code: str = Form(...), name: Union[str, None] = Form(None), gender: Union[str, None] = Form(None, regex="^male$|female$"),
                           date_of_birth: Union[datetime.date, None] = Form(None), description: Union[str, None] = Form(None), image: Union[UploadFile, None] = File(None),
                               current_user: User=Depends(get_current_active_user)):
    try:
        apifunction = 'voicebio_create_user'
        name_service = 'voice_bio_v2'
        gw = 'api/voicebio/v2/user/create'
        result = VOICE_BIO_V2_Controllers.creat_update_delete_user(current_user, apifunction, name_service, gw, user_code,
                                                            name, gender, date_of_birth, description, image)
        return result
    except:
        logging.info('VOICE BIO V2 - CREATE USER -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - CREATE USER -> Internal Server Error!')

@VOICE_BIO_V2.post('/api/voicebio/v2/user/update', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_update_user(user_code: str = Form(...), name: Union[str, None] = Form(None), gender: Union[str, None] = Form(None, regex="^male$|female$"),
                           date_of_birth: Union[datetime.date, None] = Form(None), description: Union[str, None] = Form(None), image: Union[UploadFile,None] = File(None),
                               current_user: User = Depends(get_current_active_user)):
    try:
        apifunction = 'voicebio_update_user'
        name_service = 'voice_bio_v2'
        gw = 'api/voicebio/v2/user/update'
        result = VOICE_BIO_V2_Controllers.creat_update_delete_user(current_user, apifunction, name_service, gw, user_code, name, gender, date_of_birth, description, image)
        return result
    except:
        logging.info('VOICE BIO V2 - UPDATE USER -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - UPDATE USER -> Internal Server Error!')

@VOICE_BIO_V2.delete('/api/voicebio/v2/user/delete', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_delete_user(user_code: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        apifunction = 'voicebio_delete_user'
        name_service = 'voice_bio_v2'
        gw = 'api/voicebio/v2/user/delete'
        result = VOICE_BIO_V2_Controllers.creat_update_delete_user(current_user, apifunction, name_service, gw, user_code)
        return result
    except:
        logging.info('VOICE BIO V2 - DELETE USER -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - DELETE USER -> Internal Server Error!')

@VOICE_BIO_V2.post('/api/voicebio/v2/enroll/addfile', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_enroll_addfile(user_code: str = Form(...), file: Union[UploadFile, None] = File(None), audio_url: Union[str, None] = Form(None), is_filter: Union[bool, None] = Form(False),
                                  current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            url = General_control.get_link_function_service('voicebio_enroll_addfile', 'voice_bio_v2')
            url_gw = setting.BASE_URL + 'api/voicebio/v2/enroll/addfile'
            service_id = str(mydb.services.find_one({'sign': 'voice_bio_v2'}).get('_id'))

            response_error = {
                'status_code': 7,
                'msg': f'Không được thiếu đồng thời cả hai trường thông tin File và Audio_Url trong một lần yêu cầu'
            }
            client_request = {
                'user_code': user_code,
                'is_filter': is_filter
            }
            files = []
            if file is None:
                if audio_url is None:
                    return response_error
                client_request['audio_url'] = audio_url
            else:
                if file.filename == '':
                    if audio_url is None:
                        return response_error
                    client_request['audio_url'] = audio_url
                else:
                    client_request['file'] = file.filename
                    if audio_url is not None:
                        response_error = {
                            'status_code': 7,
                            'msg': f'Chỉ chấp nhận một File hoặc một Audio_Url cho mỗi lần yêu cầu!'
                        }
                        return response_error

                    file_location = f'Manage/file/{file.filename}'
                    with open(file_location, 'wb+') as file_object:
                        file_object.write(file.file.read())
                    files = [
                        ('file', (file.filename, open(file_location, 'rb'), file.content_type))
                    ]
            #Kiểm tra xem số lượng request còn hay không
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                         General_control.getNOW(),
                                         url, client_request, client_response, '', '', url_gw)
                if file is not None:
                    if (file.filename != '') and (os.path.exists(file_location)):
                        files[0][1][1].close()
                        os.remove(file_location)
                return client_response

            #Chuẩn bị parameters để call APICORE
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            payload = VOICE_BIO_V2_Controllers.delete_none(client_request)
            response = requests.post(url=url, data=payload, headers=headers, files=files)
            json_res = response.json()
            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(),
                                     url, payload, json_res, payload, json_res, url_gw)
            if file:
                if (file.filename != '') and (os.path.exists(file_location)):
                    files[0][1][1].close()
                    os.remove(file_location)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')
    except:
        logging.info('VOICE BIO V2 - ADD NEW FILE -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - ADD NEW FILE ->Internal Server Error!')

@VOICE_BIO_V2.delete('/api/voicebio/v2/enroll/delefile', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_enroll_delefile(user_code: str = Form(...), file_code: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            client_request = {
                'user_code': user_code,
                'file_code': file_code
            }
            url = General_control.get_link_function_service('voicebio_enroll_delefile', 'voice_bio_v2')
            url_gw = setting.BASE_URL + 'api/voicebio/v2/enroll/delefile'
            service_id = str(mydb.services.find_one({'sign': 'voice_bio_v2'}).get('_id'))
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                         General_control.getNOW(),
                                         url, client_request, client_response, '', '', url_gw)
                return client_response
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            files = []
            payload = client_request
            response = requests.post(url=url, headers=headers, data=payload, files=files)
            json_res = response.json()
            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(),
                                     url, payload, json_res, payload, json_res, url_gw)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')
    except:
        logging.info('VOICE BIO V2 - DELETE FILE -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - DELETE FILE -> Internal Server Error!')

@VOICE_BIO_V2.post('/api/voicebio/v2/enroll/list_file', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_enroll_listfile(user_code: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            url = General_control.get_link_function_service('voicebio_enroll_listfile', 'voice_bio_v2')
            url_gw = setting.BASE_URL + 'api/voicebio/v2/enroll/list_file'
            client_request = {
                'user_code': user_code
            }
            service_id = str(mydb.services.find_one({'sign':'voice_bio_v2'}).get('_id'))
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                         General_control.getNOW(),
                                         url, client_request, client_response, '', '', url_gw)
                return client_response

            files = []
            payload = client_request
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            response = requests.post(url=url, headers=headers, files=files, data=payload)
            json_res = response.json()
            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(),
                                     url, payload, json_res, payload, json_res, url_gw)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')
    except:
        logging.info('VOICE BIO V2 - LIST FILE -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - LIST FILE -> Internal Server Error!')
@VOICE_BIO_V2.delete('/api/voicebio/v2/enroll/user/reset', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_enroll_user_reset(user_code: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            url = General_control.get_link_function_service('voicebio_enroll_user_reset', 'voice_bio_v2')
            url_gw = setting.BASE_URL + 'api/voicebio/v2/enroll/user/reset'
            service_id = str(mydb.services.find_one({'sign':'voice_bio_v2'}).get('_id'))
            client_request = {
                'user_code': user_code
            }
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                             General_control.getNOW(),
                                             url, client_request, client_response, '', '', url_gw)
                return client_response
            files = []
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            payload = client_request
            response = requests.post(url=url, headers=headers, data=payload, files=files)
            json_res = response.json()
            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                General_control.getNOW(), url, payload, json_res, payload, json_res, url_gw)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')

    except:
        logging.info('VOICE BIO V2 - DELETE ALL FILE -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - DELETE ALL FILE -> Internal Server Error!')

#Api thực hiện đăng ký model cho user từ các file giọng mẫu
@VOICE_BIO_V2.post('/api/voicebio/v2/enroll/user/do_enroll', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_enroll_user_doenroll(user_code: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            url = General_control.get_link_function_service('voicebio_enroll_user_doenroll', 'voice_bio_v2')
            url_gw = setting.BASE_URL + '/api/voicebio/v2/enroll/user/do_enroll'
            service_id = str(mydb.services.find_one({'sign': 'voice_bio_v2'}).get('_id'))
            client_request = {
                'user_code': user_code
            }
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                         General_control.getNOW(),
                                         url, client_request, client_response, '', '', url_gw)
                return client_response
            files = []
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            payload = client_request
            response = requests.post(url=url, headers=headers, data=payload, files=files)
            json_res = response.json()
            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(), url, payload, json_res, payload, json_res, url_gw)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')
    except:
        logging.info('VOICE BIO V2 - DO ENROLL USER -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - DO ENROLL USER -> Internal Server Error!')

@VOICE_BIO_V2.post('/api/voicebio/v2/user/verify/do_verify', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_user_verify(user_code: str = Form(...), file: Union[UploadFile, None] = File(None), audio_url: Union[str, None] = Form(None), is_filter: Union[bool, None] = Form(False),
                                    is_anti_spoof: Union[bool, None] = Form(False), threshold: Union[float, None] = Form(None), current_user: User = Depends(get_current_active_user)):
    try:
        if VOICE_BIO_V2_Controllers.check_token():
            url = General_control.get_link_function_service('voicebio_user_verify', 'voice_bio_v2')
            url_gw = setting.BASE_URL + 'api/voicebio/v2/user/verify/do_verify'
            service_id = str(mydb.services.find_one({'sign': 'voice_bio_v2'}).get('_id'))

            response_error = {
                'status_code': 7,
                'msg': f'Không được thiếu đồng thời cả hai trường thông tin File và Audio_Url trong một lần yêu cầu'
            }
            client_request = {
                'user_code': user_code,
                'is_filter': is_filter,
                'is_anti_spoof': is_anti_spoof,
                'threshold': threshold
            }
            files = []
            if file is None:
                if audio_url is None:
                    return response_error
                client_request['audio_url'] = audio_url
            else:
                if file.filename == '':
                    if audio_url is None:
                        return response_error
                    client_request['audio_url'] = audio_url
                else:
                    client_request['file'] = file.filename
                    if audio_url is not None:
                        response_error = {
                            'status_code': 7,
                            'msg': f'Chỉ chấp nhận một File hoặc một Audio_Url cho mỗi lần yêu cầu!'
                        }
                        return response_error

                    file_location = f'Manage/file/{file.filename}'
                    with open(file_location, 'wb+') as file_object:
                        file_object.write(file.file.read())
                    files = [
                        ('file', (file.filename, open(file_location, 'rb'), file.content_type))
                    ]
            # Kiểm tra xem số lượng request còn hay không
            if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
                client_response = {
                    'status_code': 100,
                    'msg': 'Too Limit'
                }
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                         General_control.getNOW(),
                                         url, client_request, client_response, '', '', url_gw)
                if file is not None:
                    if (file.filename != '') and (os.path.exists(file_location)):
                        files[0][1][1].close()
                        os.remove(file_location)
                return client_response
            # Chuẩn bị parameters để call APICORE
            token = VOICE_BIO_V2_Controllers.TOKEN_8k
            headers = {
                'Authorization': f'Bearer {token}'
            }
            payload = client_request
            response = requests.post(url=url, data=payload, headers=headers, files=files)
            json_res = response.json()

            if response.status_code == 200:
                if json_res.get('status') == 0:
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'VOICEBIO_V2',
                                     General_control.getNOW(),
                                     url, payload, json_res, payload, json_res, url_gw)
            if file:
                if (file.filename != '') and (os.path.exists(file_location)):
                    files[0][1][1].close()
                    os.remove(file_location)
            return json_res
        else:
            logging.info('VoiceBio Version 2 CORE -> ERROR: {}'.format(traceback.format_exc()))
            return HTTPException(status_code=500, detail='VoiceBio Version 2 CORE -> ERROR!')
    except:
        logging.info('VOICE BIO V2 - DO VERIFY -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='VOICE BIO V2 - DO VERIRY -> Internal Server Error!')