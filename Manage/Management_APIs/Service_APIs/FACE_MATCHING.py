import os

from Manage import setting
from Manage.Management_APIs.Controller_APIs import FACE_MATCHING_Controllers, General_control
import requests
from fastapi import HTTPException, APIRouter, Request, File, Form, Depends, UploadFile, Query
from typing import List, Optional, Union
from fastapi_limiter.depends import RateLimiter
from Manage.mongo_connect import mongo_create
from Manage.Management_APIs.Schemas.Schemas_share import User
import logging
import traceback
from Manage.Authentication.Token import get_current_active_user

mydb = mongo_create()

FACE_MATCHING = APIRouter(tags=['FACE MATCHING'])

@FACE_MATCHING.get('/v3/ekyc/url/verification', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ekyc_facematching_url(img1: Union[str], img2: Union[str], type1: str = Query(regex = "^portrait$|card$"), current_user: User = Depends(get_current_active_user)):
    try:
        format_type = 'url'
        url = General_control.get_link_function_service('ekyc_facematching_url', 'face_matching_v3')
        url_gw = setting.BASE_URL + 'v3/ekyc/url/verification'
        client_request = {
            'img1': img1,
            'img2': img2,
            'type1': type1,
            'format_type': format_type
        }
        service_id = str(mydb.services.find_one({'sign':'face_matching_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too Limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'FACE MATCHING', General_control.getNOW(),
                                     url, client_request, client_response, '', '',url_gw)
            return client_response
        if (not img1) or (not img2):
            client_response = {
                    'status_code': 7,
                    'msg': 'Không được để trống url các ảnh!'
                }
            return client_response

        api_key, api_secret = FACE_MATCHING_Controllers.get_authorization_facematching_v3()
        format_url = '%s?img1=%s&img2=%s&type1=%s&format_type=%s'%(url,img1,img2,type1,format_type)

        response = requests.get(url=format_url, auth=(api_key,api_secret))
        json_req = response.json()

        if json_req.get('errorCode') == '0':
            General_control.decrease_remaining_request(current_user.get('_id'),service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'),'FACE MATCHING',
                                 General_control.getNOW(),url, client_request, json_req, client_request,json_req,url_gw)

        return json_req

    except:
        logging.info('FACE MATCHING URL - ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='FACE MATCHING URL - Internal Service Error!')

@FACE_MATCHING.post('/v3/ekyc/file/verification', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ekyc_facematching_file(img1: UploadFile = File(...), img2: UploadFile = File(...), type1: str = Query(regex = "^portrait$|card$"), current_user: User = Depends(get_current_active_user)):
    try:
        format_type = 'file'
        url = General_control.get_link_function_service('ekyc_facematching_file', 'face_matching_v3')
        url_gw = setting.BASE_URL + 'v3/ekyc/url/verification'
        client_request = {
            'img1': img1.filename,
            'img2': img2.filename,
            'type1': type1,
            'format_type': format_type
        }
        service_id = str(mydb.services.find_one({'sign': 'face_matching_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too Limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'FACE MATCHING', General_control.getNOW(),
                                     url, client_request, client_response, '', '',url_gw)
            return client_response
        if img1.filename is None or img2.filename is None:
            client_response = {
                'status_code': 7,
                'msg': 'Không được để trống file các ảnh!'
            }
            return client_response

        api_key, api_secret = FACE_MATCHING_Controllers.get_authorization_facematching_v3()
        format_url = '%s?type1=%s&format_type=%s' % (url, type1, format_type)
        file_location = 'Manage/file/'
        with open(os.path.join(file_location, img1.filename), 'wb+') as file_object:
            file_object.write(img1.file.read())
        with open(os.path.join(file_location, img2.filename), 'wb+') as file_object:
            file_object.write(img2.file.read())
        files = {
            'img1': open(os.path.join(file_location, img1.filename), 'rb'),
            'img2': open(os.path.join(file_location, img2.filename), 'rb')
        }
        response = requests.post(url=format_url, auth=(api_key,api_secret), files=files)
        json_res = response.json()
        if json_res.get('errorCode') == '0':
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'),'FACE MATCHING', General_control.getNOW(),
                                 url, client_request, json_res, client_request, json_res, url_gw)

        if os.path.exists(os.path.join('Manage/file/', img1.filename)):
            files['img1'].close()
            os.remove(os.path.join('Manage/file/', img1.filename))
        if os.path.exists(os.path.join('Manage/file/', img2.filename)):
            files['img2'].close()
            os.remove(os.path.join('Manage/file/', img2.filename))
        return json_res

    except:
        logging.info('FACE MATCHING FILE - ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='FACE MATCHING FILE - Internal Service Error!')

@FACE_MATCHING.post('/v3/ekyc/base64/verification', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ekyc_facematching_base64(img1: str = Form(...), img2: str = Form(...), type1: str = Query(regex="^portrait$|card$"), current_user: User = Depends(get_current_active_user)):
    try:
        if (img1 is None) or (img2 is None):
            client_response = {
                'status_code': 7,
                'msg': 'Không được để trống các trường thông tin!'
            }
            return client_response

        format_type = 'base64'
        url = General_control.get_link_function_service('ekyc_facematching_base64','face_matching_v3')
        url_gw = setting.BASE_URL + 'v3/ekyc/base64/verification'
        client_request = {
            'type1': type1,
            'format_type': format_type
        }
        service_id = str(mydb.services.find_one({'sign':'face_matching_v3'}).get('_id'))

        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too Limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'FACE MATCHING',
                                     General_control.getNOW(),
                                     url, client_request, client_response, '', '', url_gw)
            return client_response

        format_url = '%s?type1=%s&format_type=%s' % (url, type1, format_type)
        api_key,api_secret = FACE_MATCHING_Controllers.get_authorization_facematching_v3()
        response = requests.post(url=format_url, auth=(api_key, api_secret), json={'img1': img1, 'img2': img2})
        json_res = response.json()
        if json_res.get('errorCode') == '0':
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)

        General_control.save_log(current_user.get('_id'), current_user.get('username'), 'FACE MATCHING',
                                General_control.getNOW(), url, client_request, json_res, client_request, json_res, url_gw)

        return response.json()
    except:
        logging.info('FACE MATCHING BASE64 - ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='FACE MATCHING BASE64 - Internal Service Error!')
