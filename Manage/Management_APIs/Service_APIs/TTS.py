import datetime

from fastapi import Depends, APIRouter, Form, HTTPException
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
from Manage.mongo_connect import mongo_create
from Manage.Management_APIs.Controller_APIs import General_control, TTS_Controllers
import requests
from Manage import setting
import logging
import traceback
from bson.objectid import ObjectId

mydb = mongo_create()
TTS = APIRouter(tags=['TTS'])

@TTS.get('/tts/voices', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_voices(current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        url = General_control.get_link_function_service('tts_voices', 'tts')
        url_gw = setting.BASE_URL + '/tts/voices'

        service_id = str(mydb.services.find_one({'sign': 'tts'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                         General_control.getNOW(), url, '', client_response, '', '', url_gw)
            return client_response

        payload = {}
        headers = {}
        response = requests.get(url=url, headers=headers, data=payload)

        client_response = response.json()

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                     General_control.getNOW(), url, '', client_response, '', client_response, url_gw)

        return client_response
    except:
        logging.info("TTS service - ERROR!: {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service - Get list VoiceID -> Internal Service Error!")

@TTS.post('/tts/path', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_path(text: str = Form(...), voiceId: str = Form(...), volumn: float = Form(None), speed: float = Form(None),
                   current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        apifunction = "tts_path"
        name_service = "tts"
        subdirectory = "tts/path"
        msg_error = "TTS Service - Audio URL -> Internal Service Error!"
        return TTS_Controllers.processing(text, voiceId, current_user, apifunction, name_service, subdirectory, msg_error, volumn, speed)
    except:
        logging.info("TTS Service ERROR! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service -> Internal Service Error!")

@TTS.post('/tts/path/8k', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_path(text: str = Form(...), voiceId: str = Form(...), volumn: float = Form(None), speed: float = Form(None),
                   current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        apifunction = "tts_path_v1"
        name_service = "tts"
        subdirectory = "tts/path/8k"
        msg_error = "TTS Service - Audio URL 8K -> Internal Service Error!"
        return TTS_Controllers.processing(text, voiceId, current_user, apifunction, name_service, subdirectory, msg_error, volumn, speed)
    except:
        logging.info("TTS Service ERROR! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service -> Internal Service Error!")

@TTS.post('/tts/task/submit', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_task_submit(text: str = Form(...), voiceId: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        apifunction = "tts_task_submit"
        name_service = "tts"
        subdirectory = "tts/task/submit"
        msg_error = "TTS Service - Audio URL Submit Task -> Internal Service Error!"
        return TTS_Controllers.processing(text, voiceId, current_user, apifunction, name_service,
                                          subdirectory, msg_error)

    except:
        logging.info("TTS Service ERROR! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service - Submit Task -> Internal Service Error!")

@TTS.get('/tts/task/get/{task_id}', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_task_get(task_id: str, current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        url = General_control.get_link_function_service('tts_task_get', 'tts') + task_id
        url_gw = setting.BASE_URL + f'/tts/task/get/{task_id}'

        client_request = {
            'task_id': task_id
        }

        service_id = str(mydb.services.find_one({'sign': 'tts'}).get('_id'))

        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        payload = {}
        files = {}
        headers = {}

        response = requests.get(url=url, headers=headers, data=payload, files=files)
        res_json = response.json()

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'tts',
                                 General_control.getNOW(), url, client_request, res_json, client_request,
                                 res_json, url_gw)

        return res_json
    except:
        logging.info("TTS Service ERROR! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service - Get Task -> Internal Service Error!")

#API thống kê tổng số lượng request, tổng số ký tự trong một khoảng thời gian
@TTS.get('/tts/statistics/', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def tts_statistics(start_time: str = Form(...), end_time: str = Form(...), user_id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        start_time = datetime.datetime.strptime(start_time,'%d/%m/%Y %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time,'%d/%m/%Y %H:%M:%S')
        #convert datetime to timestamp

        start_time = int(datetime.datetime.timestamp(start_time))
        end_time = int(datetime.datetime.timestamp(end_time))
        results = TTS_Controllers.statistics(start_time, end_time, user_id)
        return HTTPException(status_code=200, detail=results)
    except:
        logging.info("TTS Service - Statistics ERROR ! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="TTS Service - Statistics -> Internal Server Error!")

@TTS.delete('/delete/document/api_gateway', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def delete_document(start_time: str = Form(None), end_time: str = Form(...), current_user: Schemas_share.User = Depends((get_current_active_user))):
    try:
        if current_user.get('api_key') == 'maitrongjthuaanf':
            end_time = datetime.datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')
            end_time = datetime.datetime.timestamp(end_time)
            if start_time:
                start_time = datetime.datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')
                start_time = datetime.datetime.timestamp(start_time)

                filter = {
                    'user_id': ObjectId('62130828d00a413cbb8c7c9f'),
                    'service': 'asr',
                    'link_gw': {'$regex': 'get_task/{task_id}'},
                    'timestamp': {'$gte': start_time, '$lte': end_time}
                }
            else:
                filter = {
                    'user_id': ObjectId('62130828d00a413cbb8c7c9f'),
                    'service': 'asr',
                    'link_gw': {'$regex': 'get_task/{task_id}'},
                    'timestamp': {'$lte': end_time}
                }

            mydb.api_logs.delete_many(filter)
            return True
        else:
            return HTTPException(status_code=400, detail="Bạn không được cấp quyền để truy vấn database!")
    except:
        logging.info("DELETE Collection api_logs - ERROR ! - {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="DELETE Collection api_logs -> Internal Server Error!")
