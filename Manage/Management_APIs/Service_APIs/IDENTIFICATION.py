from fastapi import APIRouter, Depends, Form
from Manage.Authentication.Token import get_current_active_user
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Controller_APIs import General_control, IDENTIFICATION_Controllers
from Manage.mongo_connect import mydb
from Manage.Management_APIs.Schemas import Schemas_share
import requests
from Manage import setting

IDENTIFICATION=APIRouter(tags=['IDENTIFICATION'])

@IDENTIFICATION.post("/identification/siv2", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def identification_siv2(id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = IDENTIFICATION_Controllers.get_link_function_identification('identification_siv2')
    url_gw = setting.BASE_URL + "/identification/siv2"
    client_request = {
        'id': id
    }
    token = mydb.services.find_one({'sign': 'identification'}).get('token')
    service_id = str(mydb.services.find_one(
        {'sign': 'identification'}).get('_id'))

    if IDENTIFICATION_Controllers.validation_check_identification_id(id) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng CMND, CCCD"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)

    payload = "{\"ID\":\"" + id + "\"}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }
    name_service = 'siv2'
    result_check = IDENTIFICATION_Controllers.check_identification_in_db(id, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return response

    response = requests.request("POST", url, headers=headers, data=payload)
    if result_check == 'push_service':
        IDENTIFICATION_Controllers.user_identification_push_service(
            id, name_service, payload, response.json())
    elif result_check == 'update':
        IDENTIFICATION_Controllers.user_identification_update_service(
            id, name_service, payload, response.json())
    else:  # Create user
        IDENTIFICATION_Controllers.user_identification_create_user(
            id, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    return (response.json())
###
@IDENTIFICATION.post("/identification/siv4", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def identification_siv4(id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = IDENTIFICATION_Controllers.get_link_function_identification('identification_siv4')
    url_gw = setting.BASE_URL + "/identification/siv4"
    client_request = {
        'id': id
    }
    token = mydb.services.find_one({'sign': 'identification'}).get('token')
    service_id = str(mydb.services.find_one(
        {'sign': 'identification'}).get('_id'))
    if IDENTIFICATION_Controllers.validation_check_identification_id(id) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng CMND, CCCD"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = "{\"ID\":\"" + id + "\"}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }

    name_service = 'siv4'
    result_check = IDENTIFICATION_Controllers.check_identification_in_db(id, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return response

    response = requests.request("POST", url, headers=headers, data=payload)
    if result_check == 'push_service':
        IDENTIFICATION_Controllers.user_identification_push_service(
            id, name_service, payload, response.json())
    elif result_check == 'update':
        IDENTIFICATION_Controllers.user_identification_update_service(
            id, name_service, payload, response.json())
    else:  # Create user
        IDENTIFICATION_Controllers.user_identification_create_user(
            id, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    return (response.json())

@IDENTIFICATION.post("/identification/gfi", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def identification_gfi(id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = IDENTIFICATION_Controllers.get_link_function_identification('identification_gfi')
    url_gw = setting.BASE_URL + "/identification/gfi"
    client_request = {
        'id': id
    }
    token = mydb.services.find_one({'sign': 'identification'}).get('token')
    service_id = str(mydb.services.find_one(
        {'sign': 'identification'}).get('_id'))
    if IDENTIFICATION_Controllers.validation_check_identification_id(id) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng CMND, CCCD"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = "{\"ID\":\"" + id + "\"}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }

    name_service = 'gfi'
    result_check = IDENTIFICATION_Controllers.check_identification_in_db(id, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return response

    response = requests.request("POST", url, headers=headers, data=payload)
    if result_check == 'push_service':
        IDENTIFICATION_Controllers.user_identification_push_service(
            id, name_service, payload, response.json())
    elif result_check == 'update':
        IDENTIFICATION_Controllers.user_identification_update_service(
            id, name_service, payload, response.json())
    else:  # Create user
        IDENTIFICATION_Controllers.user_identification_create_user(
            id, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    return (response.json())

@IDENTIFICATION.post("/identification/mdc", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def identification_mdc(id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = IDENTIFICATION_Controllers.get_link_function_identification('identification_mdc')
    url_gw = setting.BASE_URL + "/identification/mdc"
    client_request = {
        'id': id
    }
    token = mydb.services.find_one({'sign': 'identification'}).get('token')
    service_id = str(mydb.services.find_one(
        {'sign': 'identification'}).get('_id'))
    if IDENTIFICATION_Controllers.validation_check_identification_id(id) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng CMND, CCCD"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    payload = "{\"ID\":\"" + id + "\"}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }

    name_service = 'mdc'
    result_check = IDENTIFICATION_Controllers.check_identification_in_db(id, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'identification', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return response

    response = requests.request("POST", url, headers=headers, data=payload)
    if result_check == 'push_service':
        IDENTIFICATION_Controllers.user_identification_push_service(
            id, name_service, payload, response.json())
    elif result_check == 'update':
        IDENTIFICATION_Controllers.user_identification_update_service(
            id, name_service, payload, response.json())
    else:  # Create user
        IDENTIFICATION_Controllers.user_identification_create_user(
            id, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'identification',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    return (response.json())