#Dịch vụ tính phí, đăng ký bảo hiểm xe máy
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi_limiter.depends import RateLimiter
from Manage import setting
import requests
import logging
import traceback
from Manage.Management_APIs.Controller_APIs import BAO_VIET_Controllers, General_control
from Manage import mongo_connect
from Manage.Management_APIs.Schemas.Schemas_share import User
from Manage.Authentication.Token import get_current_active_user

mydb = mongo_connect.mongo_create()
BAO_VIET = APIRouter(tags=['BAO VIET'])

@BAO_VIET.post('/api/agency/product/moto/premium', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def baoviet_premium(request: Request, current_user: User = Depends(get_current_active_user)):
    try:
        json_req = await request.json()
        client_request = {
            'request': json_req
        }

        url = General_control.get_link_function_service('premium','bao_viet')
        url_gw = setting.BASE_URL + 'api/agency/product/moto/premium'

        service_id = str(mydb.services.find_one({'sign':'bao_viet'}).get('_id'))

        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': "Too Limit"
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'BAO VIET',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response
        api_token = BAO_VIET_Controllers.baoviet_get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.post(url=url, headers=headers, json=json_req)
        #Mai sau có tài liệu chuẩn của bên BAO VIET về chuẩn đầu ra của response trả về thì sẽ bắt lỗi ở đoạn trừ request đi 1
        General_control.decrease_remaining_request(current_user.get('_id'), service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'), 'BAO VIET',
                                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)

        return response.json()
    except:
        logging.info('BAO VIET Service - Premium -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='BAO VIET Service - Internal Service Error!')


@BAO_VIET.post('/api/agency/product/moto/createPolicyMedia', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def baoviet_createPolicyMedia(request: Request, current_user: User = Depends(get_current_active_user)):
    try:
        json_req = await request.json()
        url = General_control.get_link_function_service('createPolicyMedia','bao_viet')
        url_gw = setting.BASE_URL + 'api/agency/product/moto/createPolicyMedia'

        client_request = {
            'request': json_req
        }
        service_id = str(mydb.services.find_one({'sign':'bao_viet'}).get('_id'))
        if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
            client_response = {
                'status_code': 100,
                'msg': 'Too limit'
            }
            General_control.save_log(current_user.get('_id'), current_user.get('username'), 'BAO VIET',
                                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
            return client_response

        api_token = BAO_VIET_Controllers.baoviet_get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}

        response = requests.post(url=url, json=json_req, headers=headers)

        #Mai sau có tài liệu chuẩn của bên BAO VIET về chuẩn đầu ra của response trả về thì sẽ bắt lỗi ở đoạn trừ request đi 1
        General_control.decrease_remaining_request(current_user.get('_id'), service_id)
        General_control.save_log(current_user.get('_id'), current_user.get('username'), 'BAO VIET',
                                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)

        return response.json()
    except:
        logging.info('BAO VIET Service - CreatePolicyMedia -> ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='BAO VIET Service - Internal Service Error!')