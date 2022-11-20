from fastapi import Depends, Form, APIRouter, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Management_APIs.Controller_APIs import General_control, VOICE_BIO_Controllers
from Manage.mongo_connect import mydb
import requests
import os
import json
from Manage import setting

VOICE_BIO=APIRouter(tags=['VoiceBio'])


@VOICE_BIO.post("/voicebio/create_user", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_create_user(name: str = Form(...), phone: str = Form(...), email: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    insert_data = {
        'name': name,
        'phone': phone,
        'email': email,
        'partner_id': current_user.get('_id'),
        'created_at': General_control.getNOW()
    }

    url = setting.BASE_URL+ "/voicebio/create_user"
    url_gw = setting.BASE_URL + "/voicebio/create_user"
    service_id = str(mydb.services.find_one({'sign': 'voicebio'}).get('_id'))
    client_request = {
        'name': name,
        'phone': phone,
        'email': email
    }

    phone_is_exist = mydb.user_voicebio.find_one({'phone': phone})
    if phone_is_exist:
        response = {"status_code": 3, "msg": "Số điện thoại đã tồn tại"}
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                     General_control.getNOW(), url, insert_data, response, '', '', url_gw)
        return response

    email_is_exist = mydb.user_voicebio.find_one({'email': email})
    if email_is_exist:
        response = {"status_code": 4, "msg": "Email đã tồn tại"}
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                     General_control.getNOW(), url, insert_data, response, '', '', url_gw)
        return response

    if VOICE_BIO_Controllers.get_remaining_voice(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 102,
            'msg': 'Bạn đã sử dụng hết số lượng giọng nói cho phép'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    VOICE_BIO_Controllers.decrease_remaining_voice(current_user.get('_id'), service_id)

    x = mydb.user_voicebio.insert_one(insert_data)
    response = {
        "status_code": 1,
        "msg": "Thêm user thành công",
        '_id': x.inserted_id,
        'name': name,
        'phone': phone,
        'email': email
    }
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                 General_control.getNOW(), url, insert_data, response, '', '', url_gw)
    return response

@VOICE_BIO.get("/voicebio/get_user", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_get_user(current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = setting.BASE_URL + "/voicebio/get_user"
    url_gw = setting.BASE_URL + "/voicebio/get_user"
    users = mydb.user_voicebio.find({'partner_id': current_user.get('_id')})
    response = {"status_code": 1, "data": list(users)}
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio', General_control.getNOW(),
                 url, '', response, '', '', url_gw)
    return response

@VOICE_BIO.delete("/voicebio/delete_user", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_delete_user(phone: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = setting.BASE_URL + "/voicebio/delete_user"
    url_gw = setting.BASE_URL + "/voicebio/delete_user"
    phone_is_exist = mydb.user_voicebio.find_one({'phone': phone})
    if phone_is_exist is None:
        response = {"status_code": 0, "msg": "Số điện thoại chưa tồn tại"}
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio', General_control.getNOW(),
                                 'https://api.smartbot.vn/voicebio/delete_user', phone, response, '', '', url_gw)
        return response
    mydb.user_voicebio.delete_one({'phone': phone})
    response = {"status_code": 1, "msg": "Xoá thành công"}
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio', General_control.getNOW(),
                             url, phone, response, '', '', url_gw)
    return response

@VOICE_BIO.post('/voicebio/check_audio', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voicebio_check_audio(file: UploadFile = File(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = VOICE_BIO_Controllers.get_link_function_voicebio('voicebio_do_enroll_16k')
    url_gw = setting.BASE_URL + '/voicebio/check_audio'
    if file:
        if file.filename == "":
            response = {"status_code": 7, "msg": "Không được để trống file"}
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                         General_control.getNOW(), url, "", response, '', '', url_gw)
            return response

    service_id = str(mydb.services.find_one(
        {'sign': 'voicebio'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    local_dir = os.getcwd()
    file_location = f"{local_dir}/file/{file.filename}"
    print(file_location)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # duration = get_duration("file/" + file.filename)
    # if duration == False:
    #     client_response = {
    #         'status_code': 8,
    #         'msg': f"File {file.filename} không thể phân tích. Yêu cầu file WAV định dạng mono PCM 16 bit"
    #     }
    #     api.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
    #              getNOW(), url, file.filename, client_response, '', '', url_gw)
    #     if os.path.exists('file/' + file.filename):
    #         os.remove('file/' + file.filename)
    #     return client_response
    # elif duration < 2 or duration > 20:
    #     client_response = {
    #         'status_code': 9,
    #         'msg': "Độ dài file yêu cầu trong khoảng từ 2s đến 20s"
    #     }
    #     api.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
    #              getNOW(), url, file.filename, client_response, '', '', url_gw)
    #     if os.path.exists('file/' + file.filename):
    #         os.remove('file/' + file.filename)
    #     return client_response

    files = [
        ('audio-files', (file.filename,
         open(os.path.join("file", file.filename), 'rb'), file.content_type))
    ]
    headers = {}

    _response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    my_request = {
        'file': file.filename
    }
    files[0][1][1].close()
    if os.path.exists('file/' + file.filename):
        pass
        #os.remove('file/' + file.filename)
    print(_response,"+++++++++++++++++++++")
    r_json = _response.json()
    embedding_path = r_json.get('embedding_path')
    code = r_json.get('code')
    if embedding_path:
        response = {"status_code": 1, "msg": "File đạt yêu cầu"}
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                     General_control.getNOW(), url, my_request, response, my_request, r_json, url_gw)
        return response
    response = {"status_code": 0, "msg": "File không đạt yêu cầu", "code": code,
                "error": VOICE_BIO_Controllers.get_message_error_voicebio(code)}
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voicebio',
                 General_control.getNOW(), url, my_request, response, my_request, r_json, url_gw)
    return response