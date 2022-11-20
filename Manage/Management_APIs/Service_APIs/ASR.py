from fastapi import APIRouter, Depends, File, Form, UploadFile
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Management_APIs.Controller_APIs import ASR_Controllers, General_control
from Manage.mongo_connect import mydb
from fastapi_limiter.depends import RateLimiter
from Manage.Authentication.Token import get_current_active_user
import os
import requests
from Manage import setting

ASR=APIRouter(tags=['ASR'])

@ASR.post("/asr/vad/channel/v1/submit_task", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v1_submit_task(file: UploadFile = File(...), callback_url: str = Form(None),
                                         current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = General_control.get_link_function_service("asr_vad_channel_v1_submit_task","asr")
    url_gw = setting.BASE_URL + "/asr/vad/channel/v1/submit_task"
    token = mydb.services.find_one({'sign': 'asr'}).get('password')

    service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

    client_request = {
        'file': file.filename,
        'callback_url': callback_url,
    }

    if file.filename == '':
        client_response = {
            'status_code': 0,
            'msg': "Không được để trống file"
        }
        General_control.save_log(current_user.get("_id"), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    limit_duration = ASR_Controllers.get_limit_duration(current_user.get('_id'), service_id)
    print(limit_duration)

    file_location = f"Manage/file/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # duration = get_duration("file/" + file.filename)
    # if duration == False:
    #     client_response = {
    #         'status_code': 8,
    #         'msg': f"File {file.filename} không thể phân tích. Yêu cầu file WAV định dạng mono PCM 16 bit"
    #     }
    #     api.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
    #              getNOW(), url, file.filename, client_response, '', '', url_gw)
    #     if os.path.exists('file/' + file.filename):
    #         os.remove('file/' + file.filename)
    #     return client_response

    # elif limit_duration != -1:
    #     if duration < 2 or duration > limit_duration:
    #         client_response = {
    #             'status_code': 9,
    #             'msg': f"Độ dài file yêu cầu trong khoảng từ 2s đến {limit_duration}s"
    #         }
    #         api.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
    #                  getNOW(), url, file.filename, client_response, '', '', url_gw)
    #         if os.path.exists('file/' + file.filename):
    #             os.remove('file/' + file.filename)
    #         return client_response

    if ASR_Controllers.get_remaining_number_file(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 101,
            'msg': 'Bạn đã sử dụng hết số lượng file cho phép'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    ASR_Controllers.decrease_remaining_number_file(current_user.get('_id'), service_id)

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {'token': token}
    if callback_url:
        payload['callback-url'] = callback_url

    files = [
        ('audio-file', (file.filename, open(os.path.join(
            "Manage/file", file.filename), 'rb'), file.content_type))
    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr', General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())


@ASR.get("/asr/vad/channel/v1/get_task/{task_id}", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v1_get_task(task_id: str, current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = General_control.get_link_function_service("asr_vad_channel_v1_get_task","asr") + task_id
    url_gw = setting.BASE_URL + f"/asr/vad/channel/v1/get_task/{task_id}"

    service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

    client_request = {
        'task_id': task_id
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    files = {}
    headers = {}

    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                 General_control.getNOW(), url, task_id, response.json(), url, response.json(), url_gw)
    return (response.json())


@ASR.post("/asr/vad/channel/v2/submit_task", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v2_submit_task(file: UploadFile = File(...), callback_url: str = Form(None),
                                         current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = General_control.get_link_function_service("asr_vad_channel_v2_submit_task","asr")
    url_gw = setting.BASE_URL + "/asr/vad/channel/v2/submit_task"

    token = mydb.services.find_one({'sign': 'asr'}).get('password')
    service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

    client_request = {
        'file': file.filename,
        'callback_url': callback_url
    }

    if file.filename == '':
        client_response = {
            'status_code': 0,
            'msg': "Không được để trống file"
        }
        General_control.save_log(current_user.get("_id"), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    limit_duration = ASR_Controllers.get_limit_duration(current_user.get('_id'), service_id)

    file_location = f"Manage/file/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # duration = get_duration("file/" + file.filename)
    # if duration == False:
    #     client_response = {
    #         'status_code': 8,
    #         'msg': f"File {file.filename} không thể phân tích. Yêu cầu file WAV định dạng mono PCM 16 bit"
    #     }
    #     api.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
    #              getNOW(), url, file.filename, client_response, '', '', url_gw)
    #     if os.path.exists('file/' + file.filename):
    #         os.remove('file/' + file.filename)
    #     return client_response

    # elif limit_duration != -1:
    #     if duration < 2 or duration > limit_duration:
    #         client_response = {
    #             'status_code': 9,
    #             'msg': f"Độ dài file yêu cầu trong khoảng từ 2s đến {limit_duration}s"
    #         }
    #         api.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
    #                  getNOW(), url, file.filename, client_response, '', '', url_gw)
    #         if os.path.exists('file/' + file.filename):
    #             os.remove('file/' + file.filename)
    #         return client_response

    if ASR_Controllers.get_remaining_number_file(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 101,
            'msg': 'Bạn đã sử dụng hết số lượng file cho phép'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    ASR_Controllers.decrease_remaining_number_file(current_user.get('_id'), service_id)

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {'token': token}
    if callback_url:
        payload['callback-url'] = callback_url

    files = [
        ('audio-file', (file.filename, open(os.path.join(
            "Manage/file", file.filename), 'rb'), file.content_type))
    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr', General_control.getNOW(), url,
                             client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())

##
@ASR.get("/asr/vad/channel/v2/get_task/{task_id}", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v2_get_task(task_id: str, current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = General_control.get_link_function_service("asr_vad_channel_v2_get_task","asr") + task_id
    url_gw = setting.BASE_URL + f"/asr/vad/channel/v2/get_task/{task_id}"
    service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

    client_request = {
        'task_id': task_id
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    files = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                 General_control.getNOW(), url, task_id, response.json(), url, response.json(), url_gw)
    return (response.json())