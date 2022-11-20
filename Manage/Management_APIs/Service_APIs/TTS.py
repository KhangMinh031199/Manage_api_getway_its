from fastapi import Depends, APIRouter, Form
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
from Manage.mongo_connect import mydb
from Manage.Management_APIs.Controller_APIs import General_control, TTS_Controllers
import requests
from Manage import setting

TTS=APIRouter(tags=['TTS'])

@TTS.get('/tts/voices', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_voices(current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = TTS_Controllers.get_link_function_tts('tts_voices')
    url_gw = setting.BASE_URL + '/tts/voices'

    service_id = str(mydb.services.find_one(
        {'sign': 'tts'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    client_response = response.json()

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                 General_control.getNOW(), url, '', client_response, '', client_response, url_gw)

    return client_response

@TTS.post('/tts/path', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_path(text: str = Form(...), voiceId: str = Form(...), volumn: float = Form(None), speed: float = Form(None),
                   current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = TTS_Controllers.get_link_function_tts('tts_path')
    url_gw = setting.BASE_URL + '/tts/path'

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

    service_id = str(mydb.services.find_one(
        {'sign': 'tts'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    remaining_character = TTS_Controllers.get_remaining_character(
        current_user.get('_id'), service_id)
    if remaining_character == -1:
        token = mydb.services.find_one({'sign': 'tts'}).get('password')

        payload = {
            'token': token,
            'text': text,
            'voiceId': voiceId,
            'volumn': volumn,
            'speed': speed,
        }
        files = [

        ]
        headers = {}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)

        client_response = response.json()

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

        return client_response

    if remaining_character < length:
        client_response = {
            'status_code': 105,
            'msg': f"Bạn không đủ số ký tự để sử dụng. Số ký tự còn lại: {remaining_character}"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    TTS_Controllers.decrease_remaining_character(
        current_user.get('_id'), service_id, length)

    token = mydb.services.find_one({'sign': 'tts'}).get('password')

    payload = {
        'token': token,
        'text': text,
        'voiceId': voiceId
    }
    files = [

    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    client_response = response.json()

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                 General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

    return client_response

@TTS.post('/tts/path/8k', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_path(text: str = Form(...), voiceId: str = Form(...), volumn: float = Form(None), speed: float = Form(None),
                   current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = TTS_Controllers.get_link_function_tts('tts_path_v1')
    url_gw = setting.BASE_URL + '/tts/path/8k'

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

    service_id = str(mydb.services.find_one(
        {'sign': 'tts'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    remaining_character = TTS_Controllers.get_remaining_character(
        current_user.get('_id'), service_id)
    if remaining_character == -1:
        token = mydb.services.find_one({'sign': 'tts'}).get('password')

        payload = {
            'token': token,
            'text': text,
            'voiceId': voiceId,
            'volumn': volumn,
            'speed': speed,
        }
        files = [

        ]
        headers = {}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)

        client_response = response.json()

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

        return client_response

    if remaining_character < length:
        client_response = {
            'status_code': 105,
            'msg': f"Bạn không đủ số ký tự để sử dụng. Số ký tự còn lại: {remaining_character}"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    TTS_Controllers.decrease_remaining_character(
        current_user.get('_id'), service_id, length)

    token = mydb.services.find_one({'sign': 'tts'}).get('password')

    payload = {
        'token': token,
        'text': text,
        'voiceId': voiceId
    }
    files = [

    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    client_response = response.json()

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                 General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

    return client_response

@TTS.post('/tts/task/submit', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_task_submit(text: str = Form(...), voiceId: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = TTS_Controllers.get_link_function_tts('tts_task_submit')
    url_gw = setting.BASE_URL + '/tts/task/submit'

    length = len(text)
    client_request = {
        'text': text,
        'voiceId': voiceId,
        'length': length
    }

    service_id = str(mydb.services.find_one(
        {'sign': 'tts'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    remaining_character = TTS_Controllers.get_remaining_character(
        current_user.get('_id'), service_id)

    token = mydb.services.find_one({'sign': 'tts'}).get('password')

    if remaining_character == -1:
        payload = {
            'token': token,
            'text': text,
            'voiceId': voiceId
        }
        files = [

        ]
        headers = {}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)

        client_response = response.json()

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

        return client_response

    if remaining_character < length:
        client_response = {
            'status_code': 105,
            'msg': f"Bạn không đủ số ký tự để sử dụng. Số ký tự còn lại: {remaining_character}"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    TTS_Controllers.decrease_remaining_character(current_user.get('_id'), service_id, length)


    payload = {
        'token': token,
        'text': text,
        'voiceId': voiceId
    }
    files = [

    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    client_response = response.json()

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                 General_control.getNOW(), url, client_request, client_response, payload, client_response, url_gw)

    return client_response

@TTS.get('/tts/task/get/{task_id}', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_task_get(task_id: str, current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = TTS_Controllers.get_link_function_tts('tts_task_get') + task_id
    url_gw = setting.BASE_URL + '/tts/task/get/{task_id}'

    client_request = {
        'task_id': task_id
    }

    service_id = str(mydb.services.find_one(
        {'sign': 'tts'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    files = {}
    headers = {}

    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files)

    client_response = response.json()

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                 General_control.getNOW(), url, client_request, client_response, client_request, client_response, url_gw)

    return client_response
