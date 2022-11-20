from fastapi import APIRouter, UploadFile, Depends, File, Form
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
import secrets
from Manage.mongo_connect import mydb
import os
import requests
from bson.objectid import ObjectId
from Manage import setting
from Manage.Management_APIs.Controller_APIs import General_control

OCR_V2=APIRouter(tags=['OCR V2'])

@OCR_V2.post("/v2/ocr/vehicle_registrations/file",  tags=["OCR V2"], dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def vehicle_registrations_input_file2(get_thumb: str, current_user: Schemas_share.User = Depends(get_current_active_user), img1: UploadFile = File(...), img2: UploadFile = File(...)):
    format_type = 'file'
    client_request = {
        'format_type': format_type,
        'get_thumb': get_thumb,
    }
    if img1:
        client_request['img1'] = img1.filename
        if img1.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if img2:
        client_request['img2'] = img2.filename
        if img2.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                         getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    file_location = f"file/{img1.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img1.file.read())

    file_location = f"file/{img2.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img2.file.read())

    ocr_v2 = mydb.services.find_one({'sign': 'ocr_v2'})
    service_id = str(ocr_v2.get('_id'))

    url = api.get_link_function_ocr_v2('vehicle_registrations_input_file2')
    url_gw = BASE_URL + '/v2/ocr/vehicle_registrations/file'
    api_key = ocr_v2.get('username')
    api_secret = ocr_v2.get('password')

    if api.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                     getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    api.decrease_remaining_request(current_user.get('_id'), service_id)

    response = requests.post(
        "%s?format_type=%s&get_thumb=%s"
        % (url, format_type, get_thumb),
        auth=(api_key, api_secret),
        files={'img1': open(os.path.join("file", img1.filename), 'rb'),
               'img2': open(os.path.join("file", img2.filename), 'rb')})
    j_response = response.json()
    api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                 getNOW(), url, client_request, j_response, client_request, j_response, url_gw)
    return j_response

@OCR_V2.post("/v2/ocr/vehicle_registration/file",  tags=["OCR V2"], dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def vehicle_registration_input_file(get_thumb: str, current_user: User = Depends(get_current_active_user), img: UploadFile = File(...)):
    format_type = 'file'
    client_request = {
        'format_type': format_type,
        'get_thumb': get_thumb,
    }
    if img:
        client_request['img'] = img.filename
        if img.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                         getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    file_location = f"file/{img.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img.file.read())

    ocr_v2 = mydb.services.find_one({'sign': 'ocr_v2'})
    service_id = str(ocr_v2.get('_id'))

    url = api.get_link_function_ocr_v2('vehicle_registration_input_file')
    url_gw = BASE_URL + '/v2/ocr/vehicle_registration/file'
    api_key = ocr_v2.get('username')
    api_secret = ocr_v2.get('password')

    if api.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': "Too limit"
        }
        api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                     getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    api.decrease_remaining_request(current_user.get('_id'), service_id)

    response = requests.post(
        "%s?format_type=%s&get_thumb=%s"
        % (url, format_type, get_thumb),
        auth=(api_key, api_secret),
        files={'img': open(os.path.join("file", img.filename), 'rb'),
               })
    j_response = response.json()
    api.save_log(current_user.get('_id'), current_user.get('name'), 'ocr_v2',
                 getNOW(), url, client_request, j_response, client_request, j_response, url_gw)
    return j_response
