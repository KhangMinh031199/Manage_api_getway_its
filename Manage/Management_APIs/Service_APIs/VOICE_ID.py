from fastapi import APIRouter, Form, File, Depends, UploadFile
from typing import List
from Manage.Authentication.Token import get_current_active_user
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Management_APIs.Controller_APIs import VOICE_ID_Controllers, General_control
from Manage.mongo_connect import mydb
import os
import json
import requests
from Manage import setting

VoiceID=APIRouter(tags=['VoiceID'])

@VoiceID.post("/voiceid/speakers/create", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_speakers_create(speaker_id: str = Form(...), files: List[UploadFile] = File(...),
                                  current_user: Schemas_share.User = Depends(get_current_active_user)):
    url_gw = setting.BASE_URL + "/voiceid/speakers/create"
    url = VOICE_ID_Controllers.get_link_function_voiceid("voiceid_speakers_create")
    user_id = int(VOICE_ID_Controllers.get_user_id_voiceid())
    client_request = {
        'speaker_id': speaker_id,
        'user_id': user_id
    }

    for file in files:
        if file.filename == '':
            client_response = {
                'status_code': 0,
                'msg': "Không được để trống file"
            }
            General_control.save_log(current_user.get("_id"), current_user.get('name'), 'voiceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if len(files) != 3:
        client_response = {
            'status_code': 0,
            'msg': "Không đủ 3 file audio"
        }
        General_control.save_log(current_user.get("_id"), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'user_id': user_id,
               'speaker_id': speaker_id}

    for file in files:
        file_location = f"Manage/file/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
    _files = [
        ('files', (files[0].filename, open(os.path.join(
            "Manage/file", files[0].filename), 'rb'), files[0].content_type)),
        ('files', (files[1].filename, open(os.path.join(
            "Manage/file", files[1].filename), 'rb'), files[1].content_type)),
        ('files', (files[2].filename, open(os.path.join(
            "Manage/file", files[2].filename), 'rb'), files[2].content_type))
    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=_files)
    print("=====Continue====")
    for file in _files:
        file[1][1].close()

    client_request['file1'] = files[0].filename
    client_request['file2'] = files[1].filename
    client_request['file3'] = files[2].filename

    for file in files:
        if os.path.exists('file/' + file.filename):
            os.remove('file/' + file.filename)

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid', General_control.getNOW(), url,
                             client_request, response.json(), client_request, response.json(), url_gw)
    VOICE_ID_Controllers.update_user_id_voiceid()
    return response.json()

###
@VoiceID.get("/voiceid/speakers", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_speakers(current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_speakers')
    url_gw = setting.BASE_URL + "/voiceid/speakers"
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, '', response.json(), '', response.json(), url_gw)
    return response.json()



@VoiceID.get("/voiceid/speakers/{speaker_id}", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_speakers_detail(speaker_id: str, current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_speakers_detail') + str(speaker_id)
    url_gw = setting.BASE_URL + f"/voiceid/speakers/{speaker_id}"
    client_request = {
        'speaker_id': speaker_id
    }

    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return response.json()


@VoiceID.put("/voiceid/speakers/update", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_speakers_update(speaker_id: str = Form(...), files: List[UploadFile] = File(...),
                                  current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_speakers_update')
    url_gw = setting.BASE_URL + "/voiceid/speakers/update"

    client_request = {
        'speaker_id': speaker_id
    }
    for file in files:
        if file.filename == '':
            client_response = {
                'status_code': 0,
                'msg': "Không được để trống file"
            }
            General_control.save_log(current_user.get("_id"), current_user.get('name'), 'voiceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if len(files) != 3:
        client_response = {
            'status_code': 0,
            'msg': "Không đủ 3 file audio"
        }
        General_control.save_log(current_user.get("_id"), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'speaker_id': speaker_id}
    for file in files:
        file_location = f"Manage/file/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

    _files = [
        ('files', (files[0].filename, open(os.path.join(
            "Manage/file", files[0].filename), 'rb'), files[0].content_type)),
        ('files', (files[1].filename, open(os.path.join(
            "Manage/file", files[1].filename), 'rb'), files[1].content_type)),
        ('files', (files[2].filename, open(os.path.join(
            "Manage/file", files[2].filename), 'rb'), files[2].content_type))
    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=_files)
    for file in _files:
        file[1][1].close()

    client_request['file1'] = files[0].filename
    client_request['file2'] = files[1].filename
    client_request['file3'] = files[2].filename

    for file in files:
        if os.path.exists('file/' + file.filename):
            os.remove('file/' + file.filename)

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid', General_control.getNOW(),
                             url, client_request, response.json(), client_request, response.json(), url_gw)
    return response.json()

######
@VoiceID.delete("/voiceid/speakers/delete", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_speakers_delete(speaker_id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_speakers_delete')
    url_gw = setting.BASE_URL + "/voiceid/speakers/delete"
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    client_request = {
        'speaker_id': speaker_id
    }
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'speaker_id': speaker_id}
    files = [

    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), '', response.json(), url_gw)
    return response.json()

####

@VoiceID.post("/voiceid/records", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_records_create(speakers: str = Form(...), file: UploadFile = File(...),
                                 current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_records_create')
    url_gw = setting.BASE_URL + "/voiceid/records"
    client_request = {
        'speakers': speakers
    }
    if file:
        if file.filename == "":
            client_response = {"status_code": 0,
                               "msg": "Không được để trống file"}
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    client_request['file'] = file.filename
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'speakers': speakers}
    file_location = f"Manage/file/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    files = [
        ('file', (file.filename, open(os.path.join(
            "Manage/file", file.filename), 'rb'), file.content_type))
    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    files[0][1][1].close()
    if os.path.exists('Manage/file/' + file.filename):
        os.remove('Manage/file/' + file.filename)

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())

#####
@VoiceID.get("/voiceid/records", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_records_list(current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_records_list')
    url_gw = setting.BASE_URL + "/voiceid/records"
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, '', response.json(), '', response.json(), url_gw)
    return (response.json())

####
@VoiceID.get("/voiceid/records/{record_id}", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_records_detail(record_id: int, current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_records_detail') + str(record_id)
    url_gw = setting.BASE_URL + F"/voiceid/records/{record_id}"
    client_request = {
        'record_id': record_id
    }
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())

###
@VoiceID.post("/voiceid/records/rerun", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_records_rerun(record_id: int = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_records_rerun')
    url_gw = setting.BASE_URL + "/voiceid/records/rerun"
    client_request = {
        'record_id': record_id
    }
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'record_id': record_id}
    files = [

    ]
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())

####
@VoiceID.delete("/voiceid/records/delete", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def voiceid_records_delete(record_id: int = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = VOICE_ID_Controllers.get_link_function_voiceid('voiceid_records_delete')
    url_gw = setting.BASE_URL + "/voiceid/records/delete"
    client_request = {
        'record_id': record_id
    }
    service_id = str(mydb.services.find_one({'sign': 'voiceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'record_id': record_id}

    files = []
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'voiceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())

