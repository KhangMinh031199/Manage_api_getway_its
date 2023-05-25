from fastapi import APIRouter, File, UploadFile, Depends, Form
from typing import Optional, Generic
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.mongo_connect import mongo_create
from Manage.Management_APIs.Controller_APIs import FACE_ID_Controllers, General_control
from fastapi_limiter.depends import RateLimiter
import secrets
import requests
from Manage.Authentication.Token import get_current_active_user
import os
from Manage import setting

mydb = mongo_create()
FaceID = APIRouter(tags=['FaceID'])

@FaceID.post("/cloudekyc/faceid/verification", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cloudekyc_faceid_verification(image_card: UploadFile = File(...), image_live: UploadFile = File(...),
                                        image_live1: Optional[UploadFile] = File(
                                            None),
                                        image_live2: Optional[UploadFile] = File(
                                            None),
                                        image_live3: Optional[UploadFile] = File(
                                            None),
                                        check_3_random_pose: Optional[int] = Form(
                                            None),
                                        check_3_straight_pose: Optional[int] = Form(
                                            None),
                                        return_feature: Optional[int] = Form(None), request_id: Optional[str] = Form(None),
                                        current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = FACE_ID_Controllers.get_link_function_faceid("cloudekyc_faceid_verification")
    url_gw = setting.BASE_URL + "/cloudekyc/faceid/verification"
    client_request = {
        'check_3_random_pose': check_3_random_pose,
        'check_3_straight_pose': check_3_straight_pose,
        'return_feature': return_feature,
        'request_id': request_id
    }
    if image_card and image_live:
        client_request['image_card'] = image_card.filename
        client_request['image_live'] = image_live.filename
        if image_card.filename == "" or image_live.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if image_live1:
        client_request['image_live1'] = image_live1.filename
        if image_live1.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if image_live2:
        client_request['image_live2'] = image_live2.filename
        if image_live2.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if image_live3:
        client_request['image_live3'] = image_live3.filename
        if image_live3.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if request_id is None:
        request_id = secrets.token_urlsafe(9)
    service_id = str(mydb.services.find_one({'sign': 'faceid'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'check_3_random_pose': check_3_random_pose,
               'check_3_straight_pose': check_3_straight_pose,
               'return_feature': return_feature,
               'request_id': request_id}
    file_location = f"Manage/file/{image_card.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image_card.file.read())
    file_location = f"Manage/file/{image_live.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image_live.file.read())

    files = [
        ('image_card', (image_card.filename, open(os.path.join(
            "Manage/file", image_card.filename), 'rb'), image_card.content_type)),
        ('image_live', (image_live.filename, open(os.path.join(
            "Manage/file", image_live.filename), 'rb'), image_live.content_type))
    ]

    if image_live1 is not None:
        file_location = f"Manage/file/{image_live1.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image_live1.file.read())
        files.append(('image_live1', (image_live1.filename, open(os.path.join(
            "Manage/file", image_live1.filename), 'rb'), image_live1.content_type)))
    if image_live2 is not None:
        file_location = f"Manage/file/{image_live2.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image_live2.file.read())
        files.append(('image_live2', (image_live2.filename, open(os.path.join(
            "Manage/file", image_live2.filename), 'rb'), image_live2.content_type)))
    if image_live3 is not None:
        file_location = f"Manage/file/{image_live3.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image_live3.file.read())
        files.append(('image_live3', (image_live3.filename, open(os.path.join(
            "Manage/file", image_live3.filename), 'rb'), image_live3.content_type)))

    key = mydb.services.find_one({'sign': 'faceid'}).get('password')
    headers = {
        'key': key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    payload.update({'image': image_card.filename,
                    'image_live': image_live.filename})
    if image_live1 is not None:
        payload.update({'image_live1': image_live1.filename})
    if image_live2 is not None:
        payload.update({'image_live2': image_live2.filename})
    if image_live3 is not None:
        payload.update({'image_live3': image_live3.filename})
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                 General_control.getNOW(), url, payload, response.json(), payload, response.json(), url_gw)
    return (response.json())


#Đăng ký khuôn mặt
@FaceID.post("/cloudekyc/faceid/register", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cloudekyc_faceid_register(image: UploadFile = File(...), unique_name: str = Form(...),
                                    person_name: Optional[str] = Form(None), force: Optional[int] = Form(None),
                                    request_id: Optional[str] = Form(None),
                                    current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = FACE_ID_Controllers.get_link_function_faceid('cloudekyc_faceid_register')

    url_gw = setting.BASE_URL + "/cloudekyc/faceid/register"

    service_id = str(mydb.services.find_one({'sign': 'faceid'}).get('_id'))

    if request_id is None:
        request_id = secrets.token_urlsafe(9)

    client_request = {
        'unique_name': unique_name,
        'person_name': person_name,
        'force': force,
        'request_id': request_id
    }

    if image:
        client_request['image'] = image.filename
        if image.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = {'unique_name': unique_name,
               'person_name': person_name,
               'force': force,
               'request_id': request_id}
    file_location = f"Manage/file/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())

    files = [
        ('image', (image.filename, open(os.path.join(
            "Manage/file", image.filename), 'rb'), image.content_type))
    ]

    key = mydb.services.find_one({'sign': 'faceid'}).get('password')
    headers = {
        'key': key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    j_response = response.json()
    files[0][1][1].close()
    if os.path.exists(f"Manage/file/{image.filename}"):
        os.remove(f"Manage/file/{image.filename}")
    #os.mkdir('file')
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                 General_control.getNOW(), url, client_request, j_response, client_request, j_response, url_gw)
    return j_response

# Xác thực khuôn mặt
@FaceID.post("/cloudekyc/faceid/recognition", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cloudekyc_faceid_recognition(image: UploadFile = File(...), request_id: Optional[str] = Form(None),
                                       current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = FACE_ID_Controllers.get_link_function_faceid('cloudekyc_faceid_recognition')
    url_gw = setting.BASE_URL + "/cloudekyc/faceid/recognition"
    service_id = str(mydb.services.find_one({'sign': 'faceid'}).get('_id'))
    if request_id is None:
        request_id = secrets.token_urlsafe(9)

    client_request = {
        'request_id': request_id
    }

    if image:
        client_request['image'] = image.filename
        if image.filename == "":
            client_response = {
                "status_code": 7,
                "msg": "Không được để trống file"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'request_id': request_id}
    file_location = f"Manage/file/{image.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(image.file.read())

    files = [
        ('image', (image.filename, open(os.path.join(
            "Manage/file",image.filename), 'rb'), image.content_type))
    ]
    print(files)
    key = mydb.services.find_one({'sign': 'faceid'}).get('password')
    headers = {
        'key': key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)

    files[0][1][1].close()
    if os.path.exists(f"Manage/file/{image.filename}"):
        os.remove(f"Manage/file/{image.filename}")
        #shutil.rmtree(f"{image.filename}")
    #os.mkdir('file')
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    return (response.json())


#Xoá thông tin ảnh đã đăng ký của khách hàng
@FaceID.delete("/cloudekyc/faceid/delete", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cloudekyc_faceid_delete(unique_name: str = Form(...), face_id: Optional[str] = Form(None),
                                  current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = FACE_ID_Controllers.get_link_function_faceid('cloudekyc_faceid_delete')
    url_gw = setting.BASE_URL + "/cloudekyc/faceid/delete"
    service_id = str(mydb.services.find_one({'sign': 'faceid'}).get('_id'))

    client_request = {
        'unique_name': unique_name,
        'face_id': face_id
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {'unique_name': unique_name,
               'face_id': face_id}
    files = [

    ]
    key = mydb.services.find_one({'sign': 'faceid'}).get('password')
    headers = {
        'key': key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    r_json = response.json()
    if r_json.get('message').get('copy_right'):
        del r_json['message']['copy_right']
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'faceid',
                 General_control.getNOW(), url, payload, r_json, payload, response.json(), url_gw)
    return (r_json)
