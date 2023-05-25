#Dịch vụ trúy vấn thông tin từ thẻ cccd bằng NFC
#Công nghệ NFC trích xuất thông tin từ thẻ cccd và API này sẽ mang những thông tin này lên kho đối chiếu

from Manage import setting
from fastapi import HTTPException, Request, APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from Manage.mongo_connect import mongo_create
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Schemas.Schemas_share import User
from Manage.Management_APIs.Controller_APIs import General_control, RAR_Controllers
import requests
import logging
import traceback

mydb = mongo_create()

RAR = APIRouter(tags=['RAR'])

@RAR.post('/rar/base64', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def EINSIGHT4(request: Request, current_user: User = Depends(get_current_active_user)):
    try:
        json_req = await request.json()
        client_request = {
            'request': json_req
        }
        url = General_control.get_link_function_service('rar_base64','rar')
        url_gw = setting.BASE_URL + '/rar/base64'

        service_id = str(mydb.services.find_one({'sign':'rar'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'RAR',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        token = str(mydb.services.find_one({'sign':'rar'}).get('token'))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(url=url, json=json_req, headers=headers)
        result = response.json()
        if result.get('success') is True:
            General_control.decrease_remaining_request(current_user.get('_id'), service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'), 'RAR',
                                 General_control.getNOW(), url, client_request, result, client_request, result, url_gw)
        return result

    except:
        logging.info("RAR service - ERROR!: {}".format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='RAR Service - EINSIGHT4 -> Internal Service Error!')
