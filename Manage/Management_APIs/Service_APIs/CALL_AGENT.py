from fastapi import APIRouter, Form, Depends
from fastapi_limiter.depends import RateLimiter
from Manage.mongo_connect import mongo_create
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Controller_APIs import CALL_AGENT_Controllers, General_control
import secrets
import requests
import json
from Manage import setting

mydb = mongo_create()

CALL_AGENT = APIRouter(tags=['Call Agent'])

@CALL_AGENT.post("/call/agent", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callagent_call_agent(hotline: str = Form(...), agent_phone: str = Form(...), called: str = Form(...), cus_id: str = Form(...), limit_time: str = Form(None),
                               current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = General_control.get_link_function_service('callagent_call_agent',"callagent")
    print(url)
    url = "http://125.212.225.71:8344/smartseller/v1/call/agent"
    url_gw = setting.BASE_URL + "/call/agent"
    service_id = str(mydb.services.find_one({'sign': 'callagent'}).get('_id'))

    client_request = {
        'hotline': hotline,
        'agent_phone': agent_phone,
        'called': called,
        'cus_id': cus_id,
        'limit_time': limit_time
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one(
        {'sign': 'callagent'}).get('username')
    token = CALL_AGENT_Controllers.get_callagent_token()
    print("=====++++=======",token)
    payload = json.dumps({
        "hotline": hotline,
        "agent_phone": agent_phone,
        "called": called,
        "cus_id": cus_id,
        "request_id": str(secrets.token_urlsafe(8)),
        "url_webhook": General_control.get_url_webhook(current_user.get('_id')),
        "is_asr": General_control.check_have_asr(current_user.get('_id')),
        "limit_time": limit_time
    })
    headers = {
        'client-id': username,
        'x-access-token': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    return (response.json())

@CALL_AGENT.get("/call/hotline/get", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callagent_hotline_get(current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = General_control.get_link_function_service('callagent_hotline_get','callagent')
    url_gw = setting.BASE_URL + "/call/hotline/get"
    service_id = str(mydb.services.find_one({'sign': 'callagent'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one(
        {'sign': 'callagent'}).get('username')
    token = CALL_AGENT_Controllers.get_callagent_token()

    payload = {}
    headers = {
        'client-id': username,
        'x-access-token': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get(
        'name'), 'callagent', General_control.getNOW(), url, '', response.json(), '', response.json(), url_gw)
    return (response.json())

@CALL_AGENT.post("/call/hotline/assign", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callagent_hotline_assign(hotline: str = Form(...), cus_id: str = Form(...),
                                   current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = General_control.get_link_function_service('callagent_hotline_assign','callagent')
    url_gw = setting.BASE_URL + "/call/hotline/assign"
    service_id = str(mydb.services.find_one({'sign': 'callagent'}).get('_id'))

    client_request = {
        'hotline': hotline,
        'cus_id': cus_id
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one(
        {'sign': 'callagent'}).get('username')
    token = CALL_AGENT_Controllers.get_callagent_token()

    payload = json.dumps({
        "hotline": hotline,
        "cus_id": cus_id
    })
    headers = {
        'client-id': username,
        'x-access-token': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)

    return (response.json())

@CALL_AGENT.post("/call/agent/register", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callagent_agent_register(agent_id: str = Form(...), name: str = Form(...), phone_no: str = Form(...), cus_id: str = Form(...),
                                   current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = General_control.get_link_function_service('callagent_agent_register','callagent')
    url_gw = setting.BASE_URL + "/call/agent/register"
    service_id = str(mydb.services.find_one({'sign': 'callagent'}).get('_id'))

    client_request = {
        'agent_id': agent_id,
        'name': name,
        'phone_no': phone_no,
        'cus_id': cus_id
    }

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response

    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one(
        {'sign': 'callagent'}).get('username')
    token = CALL_AGENT_Controllers.get_callagent_token()

    payload = json.dumps({
        "user_id": agent_id,
        "name": name,
        "phone_no": phone_no,
        "cus_id": cus_id
    })
    headers = {
        'client-id': username,
        'x-access-token': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callagent',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)

    return (response.json())

