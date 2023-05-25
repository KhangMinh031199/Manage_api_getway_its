from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Management_APIs.Controller_APIs import ASR_Controllers, General_control
from Manage.mongo_connect import mongo_create
from fastapi_limiter.depends import RateLimiter
from Manage.Authentication.Token import get_current_active_user
import os
import requests
import traceback
from Manage import setting
import logging
import datetime

mydb = mongo_create()
ASR = APIRouter(tags=['ASR'])


# Lấy thông tin file bằng task_id vs1
@ASR.get("/asr/vad/channel/v1/get_task/{task_id}",
         dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v1_get_task(task_id: str,
                                      current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = General_control.get_link_function_service("asr_vad_channel_v1_get_task", "asr") + task_id
    url_gw = setting.BASE_URL + f"/asr/vad/channel/v1/get_task/{task_id}"

    service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

    client_request = {
        'task_id': task_id
    }

    if ASR_Controllers.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                                 General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    payload = {}
    files = {}
    headers = {}

    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                             General_control.getNOW(), url, task_id, response.json(), url, response.json(), url_gw)
    return response.json()


# Đăng ký một file âm thanh mới _ version 2
@ASR.post("/asr/vad/channel/v2/submit_task",
          dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v2_submit_task(file: UploadFile = File(...), callback_url: str = Form(None),
                                         current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        url = General_control.get_link_function_service("asr_vad_channel_v2_submit_task", "asr")
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
                'msg': "Không được để trống file!"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response
        else:
            limit_duration_file = ASR_Controllers.get_limit_duration_a_file(current_user.get('_id'), service_id)
            limit_request = ASR_Controllers.get_remaining_request(current_user.get('_id'), service_id)
            remaining_duration = ASR_Controllers.get_remaining_duration(current_user.get('_id'), service_id)
            remaining_files_number = ASR_Controllers.get_remaining_number_file(current_user.get('_id'), service_id)

            file_location = f"Manage/file/{file.filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
            # Tính toán thời lượng file audio gửi về
            duration_file = ASR_Controllers.get_duration(file_location)
            if duration_file is False:
                client_response = {
                    'status_code': 8,
                    'msg': f"File {file.filename} không thể phân tích. Yêu cầu file đầu vào định dang là MP3 hoặc WAV"
                }
                General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                         General_control.getNOW(),
                                         url, file.filename, client_response, "", "", url_gw)
                return client_response
            else:
                if limit_request != -1:
                    if limit_duration_file is not None:
                        if duration_file < 1 or duration_file > (limit_duration_file * 60):
                            client_response = {
                                'status_code': 9,
                                'msg': f"Độ dài của file yêu cầu trong khoảng từ 1s đến {int(limit_duration_file) * 60}s"
                            }
                            General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                                     General_control.getNOW(), url, file.filename, client_response, "",
                                                     "", url_gw)
                            if os.path.exists(file_location):
                                os.remove(file_location)
                            return client_response
                        elif remaining_duration < round(duration_file / 60, 2):
                            client_response = {
                                'status_code': 10,
                                'msg': f"Tổng thời lượng còn lại không đủ đủ để xử lý file {file.filename} này!"
                            }
                            General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                                     General_control.getNOW(), url, file.filename, client_response, "",
                                                     "", url_gw)
                            if os.path.exists(file_location):
                                os.remove(file_location)
                            return client_response
                    if limit_request == 0:
                        client_response = {
                            'status_code': 100,
                            'msg': 'Too limit'
                        }
                        General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                                 General_control.getNOW(), url, file.filename, client_response, "",
                                                 "", url_gw)
                        if os.path.exists(file_location):
                            os.remove(file_location)
                        return client_response
                    elif remaining_files_number == 0:
                        client_response = {
                            'status_code': 101,
                            'msg': 'Bạn đã sử dụng hết số lượng file đã đăng ký!'
                        }
                        General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                                 General_control.getNOW(), url, file.filename, client_response, "",
                                                 "", url_gw)
                        if os.path.exists(file_location):
                            os.remove(file_location)
                        return client_response
                else:
                    # với limit_request == -1 là sử dụng dịch vụ full option
                    pass
                # Chuẩn bị dữ liệu để call api core
                payload = {'token': token}
                if callback_url:
                    payload['callback-url'] = callback_url
                files = [('audio-file', (file.filename, open(file_location, 'rb'), file.content_type))]
                headers = {}

                response = requests.post(url, headers=headers, files=files, data=payload)
                res = response.json()
                if res.get('status') == 0:
                    General_control.save_log(current_user.get('_id'), current_user.get('name'), "asr",
                                             General_control.getNOW(),
                                             url, client_request, res, client_request, res, url_gw,
                                             round(duration_file / 60, 2))
                    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
                    ASR_Controllers.decrease_remaining_number_file(current_user.get('_id'), service_id)
                    if limit_duration_file is not None:
                        ASR_Controllers.decrease_duration(current_user.get('_id'), service_id, duration_file)
                files[0][1][1].close()
                if os.path.exists(file_location):
                    os.remove(file_location)
                return res
    except:
        logging.info("ASR service version 2 - ERROR!: {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="ASR Service - Internal Service Error!")


##
@ASR.get("/asr/vad/channel/v2/get_task/{task_id}",
         dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_v2_get_task(task_id: str,
                                      current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        url = General_control.get_link_function_service("asr_vad_channel_v2_get_task", "asr") + task_id
        url_gw = setting.BASE_URL + f"asr/vad/channel/v2/get_task/{task_id}"
        service_id = str(mydb.services.find_one({'sign': 'asr'}).get('_id'))

        client_request = {
            'task_id': task_id
        }

        if ASR_Controllers.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        payload = {}
        files = {}
        headers = {}

        response = requests.get(url, headers=headers, files=files, data=payload)

        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'asr',
                                 General_control.getNOW(), url, task_id, response.json(), url, response.json(), url_gw)
        return response.json()
    except:
        logging.info("Get Task - ASR Service ERROR! -> {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="ASR Services - Internal Service Error!")


@ASR.post("/asr/vad/channel/statistics", tags=['ASR'],
          dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def asr_vad_channel_statistics(start_time: str = Form(...), end_time: str = Form(...), user_id: str = Form(...),
                                     current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        start_time = datetime.datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')
        start_timestamp = datetime.datetime.timestamp(start_time)
        end_time = datetime.datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')
        end_timestamp = datetime.datetime.timestamp(end_time)

        results = ASR_Controllers.get_all_duration_of_customer(start_timestamp, end_timestamp, user_id)
        return results
    except:
        logging.info("Statistics - ASR Services ERROR! -> {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="ASR Services - Internal Service Error!")

    # DONE
