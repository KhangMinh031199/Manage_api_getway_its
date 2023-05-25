import json
import os

from fastapi import APIRouter, UploadFile, Depends, File, Form, HTTPException, Request
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
from Manage.mongo_connect import mongo_create
import logging
import traceback
import requests
from bson.objectid import ObjectId
from Manage import setting
from Manage.Management_APIs.Controller_APIs import General_control, OCR_Controllers

mydb = mongo_create()
OCR_V3 = APIRouter(tags=['OCR V3'])


# Hiện tại VS3 chỉ mới update: CMND - CCCD - Passport - BLX - CMT QD - CMT SQ

# Trích xuất thông tin hai mặt với đầu vào là URL
@OCR_V3.get('/v3/ekyc/cards/url', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cards_id_get_url(img1: str, img2: str, get_thumb: str, current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = "url"
        url = General_control.get_link_function_service("cards_id_get_url", "ocr_v3")
        url_gw = setting.BASE_URL + 'v3/ekyc/cards/url'

        client_request = {
            'img1': img1,
            'img2': img2,
            'format_type': format_type,
            'get_thumb': get_thumb
        }
        services_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), services_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = "%s?img1=%s&img2=%s&format_type=%s&get_thumb=%s" % (url, img1, img2, format_type, get_thumb)
        response = requests.get(format_url, auth=(api_key, api_secret))
        res_json = response.json()
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), services_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, res_json, client_request, res_json,
                                     url_gw)
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Cards with format type is URL".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Cards with format type is URL -> Internal Service Error!")


@OCR_V3.post('/v3/ekyc/cards/file', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cards_id_post_file(get_thumb: str, img1: UploadFile = File(...), img2: UploadFile = File(...),current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = 'file'
        url = General_control.get_link_function_service('cards_id_post_file', 'ocr_v3')
        url_gw = setting.BASE_URL + '/v3/ekyc/cards/file'

        client_request = {
            'get_thumb': get_thumb,
            'format_type': format_type
        }
        client_response = {
            'status_code': 7,
            'msg': 'Không được để trống file'
        }
        if img1:
            client_request['img1'] = img1.filename
            if img1.filename == '':
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
                return client_response
        if img2:
            client_request['img2'] = img2.filename
            if img1.filename == '':
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
                return client_response

        services_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), services_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response
        # Tải ảnh về
        file_location = f'Manage/file/{img1.filename}'
        with open(file_location, 'wb+') as file_object:
            file_object.write(img1.file.read())

        file_location = f'Manage/file/{img2.filename}'
        with open(file_location, 'wb+') as file_object:
            file_object.write(img2.file.read())

        # Chuẩn bị input để call API core
        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = "%s?format_type=%s&get_thumb=%s" % (url, format_type, get_thumb)
        files = {
            'img1': open(os.path.join('Manage/file/', img1.filename), 'rb'),
            'img2': open(os.path.join('Manage/file/', img2.filename), 'rb')
        }

        response = requests.post(format_url, auth=(api_key, api_secret), files=files)
        res_json = response.json()
        # Nếu API core thực hiện thành công thì mới trừ lượt request của khách
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), services_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, res_json, client_request, res_json,
                                     url_gw)

        files['img1'].close()
        files['img2'].close()
        if os.path.exists(os.path.join('Manage/file/', img1.filename)):
            os.remove(os.path.join('Manage/file/', img1.filename))
        if os.path.exists(os.path.join('Manage/file/', img2.filename)):
            os.remove(os.path.join('Manage/file/', img2.filename))
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Cards with format type is File".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Cards with format type is File -> Internal Service Error!")

@OCR_V3.post('/v3/ekyc/cards/base64', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def cards_id_post_base64(get_thumb: str, img1: str = Form(...), img2: str = Form(...),current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = 'base64'
        url = General_control.get_link_function_service('cards_id_post_base64', 'ocr_v3')
        url_gw = setting.BASE_URL + 'v3/ekyc/cards/base64'
        client_request = {
            'fomat_type': format_type,
            'get_thumb': get_thumb
        }

        service_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        # Chuẩn bị input để call APIcore
        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = '%s?format_type=%s&get_thumb=%s' % (url, format_type, get_thumb)
        request = requests.post(url=format_url, auth=(api_key, api_secret), json={'img1': img1, 'img2': img2})
        res_json = request.json()
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3', General_control.getNOW(),
                                     url, client_request, res_json, client_request, res_json, url_gw)
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Cards with format type is Base64: {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Cards with format type is Base64 -> Internal Service Error!")

# Trích xuất thông tin từ một mặt của giấy tờ
#Đầu vào là URL
@OCR_V3.get('/v3/ekyc/card/url', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def card_id_get_url(get_thumb: str, img: str, current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = "url"
        url = General_control.get_link_function_service("card_id_get_url", "ocr_v3")
        url_gw = setting.BASE_URL + 'v3/ekyc/card/url'

        client_request = {
            'img': img,
            'format_type': format_type,
            'get_thumb': get_thumb
        }
        services_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), services_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = "%s?img=%s&format_type=%s&get_thumb=%s" % (url, img, format_type, get_thumb)
        response = requests.get(format_url, auth=(api_key, api_secret))
        res_json = response.json()
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), services_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, res_json, client_request, res_json,
                                     url_gw)
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Card with format type is URL".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Card with format type is URL -> Internal Service Error!")

@OCR_V3.post('/v3/ekyc/card/file', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def card_id_post_file(get_thumb: str, img: UploadFile = File(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = 'file'
        url = General_control.get_link_function_service('card_id_post_file', 'ocr_v3')
        url_gw = setting.BASE_URL + '/v3/ekyc/card/file'

        client_request = {
            'get_thumb': get_thumb,
            'format_type': format_type
        }

        if img:
            client_response = {
                'status_code': 7,
                'msg': 'Không được để trống file'
            }
            client_request['img'] = img.filename
            if img.filename == '':
                General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                         General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
                return client_response

        services_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), services_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response
        # Tải ảnh về
        file_location = f'Manage/file/{img.filename}'
        with open(file_location, 'wb+') as file_object:
            file_object.write(img.file.read())


        # Chuẩn bị input để call API core
        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = "%s?format_type=%s&get_thumb=%s" % (url, format_type, get_thumb)
        files = {
            'img': open(os.path.join('Manage/file/', img.filename), 'rb')
        }

        response = requests.post(format_url, auth=(api_key, api_secret), files=files)
        res_json = response.json()
        # Nếu API core thực hiện thành công thì mới trừ lượt request của khách
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), services_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, res_json, client_request, res_json,
                                     url_gw)

        files['img'].close()
        if os.path.exists(os.path.join('Manage/file/', img.filename)):
            os.remove(os.path.join('Manage/file/', img.filename))
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Card with format type is File".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Card with format type is File -> Internal Service Error!")

@OCR_V3.post('/v3/ekyc/card/base64', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def card_id_post_base64(get_thumb: str, img: str = Form(...),
                               current_user: Schemas_share.User = Depends(get_current_active_user)):
    try:
        format_type = 'base64'
        url = General_control.get_link_function_service('card_id_post_base64', 'ocr_v3')
        url_gw = setting.BASE_URL + 'v3/ekyc/card/base64'
        client_request = {
            'fomat_type': format_type,
            'get_thumb': get_thumb
        }

        service_id = str(mydb.services.find_one({'sign': 'ocr_v3'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        # Chuẩn bị input để call APIcore
        api_key, api_secret = OCR_Controllers.get_authorization_ocr_v3()
        format_url = '%s?format_type=%s&get_thumb=%s' % (url, format_type, get_thumb)
        request = requests.post(url=format_url, auth=(api_key, api_secret), json={'img': img})
        res_json = request.json()
        if res_json.get('errorCode') == "0":
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'OCR_V3', General_control.getNOW(),
                                     url, client_request, res_json, client_request, res_json, url_gw)
        return res_json
    except:
        logging.info("OCR_V3 Service ERROR! - Card with format type is Base64: {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail="OCR_V3 Service ERROR! - Card with format type is Base64 -> Internal Service Error!")
