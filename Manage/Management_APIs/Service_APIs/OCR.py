from fastapi import APIRouter, UploadFile, Depends, File, Form
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Controller_APIs import OCR_Controllers
from Manage.Management_APIs.Controller_APIs import General_control
import secrets
from Manage.mongo_connect import mydb
import os
import requests
from bson.objectid import ObjectId
from Manage import setting

OCR=APIRouter(tags=['OCR'])

@OCR.post('/ocr/id', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ocr_id(frontImg: UploadFile = File(...), backImg: UploadFile = File(None), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = OCR_Controllers.get_link_function_ocr('ocr_id')
    url_gw = setting.BASE_URL + '/ocr/id'

    msgID = secrets.token_urlsafe(9)
    client_request = {
        'msgID': msgID
    }

    if frontImg:
        client_request['frontImg'] = frontImg.filename
        if frontImg.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if backImg:
        client_request['backImg'] = backImg.filename
        if backImg.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    service_id = str(mydb.services.find_one({'sign': 'ocr'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                     General_control.getNOW(), url, client_request, client_response, "", "", url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {'msgID': msgID}
    file_location = f"Manage/file/{frontImg.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(frontImg.file.read())

    files = [
        ('frontImg', (frontImg.filename,
         open(os.path.join("Manage/file", frontImg.filename), 'rb'), frontImg.content_type))
    ]

    if backImg:
        file_location = f"Manage/file/{backImg.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(backImg.file.read())
        files.append(('backImg', (backImg.filename, open(os.path.join(
            "Manage/file", backImg.filename), 'rb'), backImg.content_type)))

    token = OCR_Controllers.get_token_ocr()
    client_id = mydb.services.find_one({'sign': 'ocr'}).get('username')
    headers = {
        'x-access-token': token,
        'client_id': client_id
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    j_response = response.json()

    files[0][1][1].close()
    if backImg:
        files[1][1][1].close()
        if os.path.exists(f"Manage/file/{backImg.filename}"):
            os.remove(f"Manage/file/{backImg.filename}")

    if os.path.exists(f"Manage/file/{frontImg.filename}"):
        os.remove(f"Manage/file/{frontImg.filename}")


    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                 General_control.getNOW(), url, client_request, j_response, payload, j_response, url_gw)
    return j_response


## Đọc thông tin giấy đăng ký xe, đăng kiểm
@OCR.post('/ocr/register', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ocr_register(image: UploadFile = File(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = OCR_Controllers.get_link_function_ocr('ocr_register')
    url_gw = setting.BASE_URL + '/ocr/register'
    msgID = secrets.token_urlsafe(9)

    client_request = {
        'msgID': msgID
    }

    if image:
        client_request['image'] = image.filename
        if image.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    service_id = str(mydb.services.find_one(
        {'sign': 'ocr'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                     General_control.getNOW(), url, client_request, client_response, "", "", url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {'msgID': msgID}
    file_location = f"Manage/file/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())

    files = [
        ('image', (image.filename,
         open(os.path.join("Manage/file", image.filename), 'rb'), image.content_type))
    ]
    token = OCR_Controllers.get_token_ocr()
    client_id = mydb.services.find_one({'sign': 'ocr'}).get('username')
    headers = {
        'x-access-token': token,
        'client_id': client_id
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    j_response = response.json()
    files[0][1][1].close()
    if os.path.exists(f"Manage/file/{image.filename}"):
        os.remove(f"Manage/file/{image.filename}")

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr', General_control.getNOW(), url, client_request, j_response, client_request, j_response, url_gw)
    return j_response


#### Giấy tờ bên lào
@OCR.post('/ocr_laos', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ocr_laos(image: UploadFile = File(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = OCR_Controllers.get_link_function_ocr('ocr_laos')
    url_gw = setting.BASE_URL + 'ocr_laos'

    msgID = secrets.token_urlsafe(9)
    client_request = {
        'msgID': msgID
    }

    if image:
        client_request['image'] = image.filename
        if image.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    service_id = str(mydb.services.find_one({'sign': 'ocr'}).get('_id'))
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                     General_control.getNOW(), url, client_request, client_response, "", "", url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {}
    file_location = f"Manage/file/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())

    files = [
        ('image', (image.filename,
         open(os.path.join("Manage/file", image.filename), 'rb'), image.content_type))
    ]

    service = mydb.services.find_one({"_id": ObjectId(service_id)})
    token = service.get('token')
    #==>token="7c8ba773-64cd-4ba5-a9bd-f035f06d0149"
    headers = {
        'api-key': token,
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    j_response = response.json()
    files[0][1][1].close()

    if os.path.exists(f"Manage/file/{image.filename}"):
        os.remove(f"Manage/file/{image.filename}")

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'ocr',
                 General_control.getNOW(), url, client_request, j_response, payload, j_response, url_gw)
    return j_response

