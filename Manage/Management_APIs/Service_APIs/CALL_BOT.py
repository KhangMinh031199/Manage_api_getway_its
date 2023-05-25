from fastapi import APIRouter, Depends, Form
from typing import List
from fastapi_limiter.depends import RateLimiter
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Schemas import Schemas_share
from Manage.Management_APIs.Controller_APIs import CALL_BOT_Controllers, General_control
import json
import secrets
import requests
from Manage.mongo_connect import mongo_create
from Manage import setting

mydb = mongo_create()
CALL_BOT=APIRouter(tags=['Call Bot'])

@CALL_BOT.post('/call/bot', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callbot_call_bot(hotline: str = Form(...), called: str = Form(...), bot_id: int = Form(...),
                           bot_region: str = Form(...), cus_id: str = Form(...), call_params: list = Depends(CALL_BOT_Controllers.call_param_dict),
                           current_user: Schemas_share.User = Depends(get_current_active_user)):

    url = CALL_BOT_Controllers.get_link_function_callbot('callbot_call_bot')
    url_gw = setting.BASE_URL + "/call/bot"
    client_request = {
        'hotline': hotline,
        'called': called,
        'bot_id': bot_id,
        'bot_region': bot_region,
        'cus_id': cus_id
    }
    service_id = str(mydb.services.find_one({'sign': 'callbot'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callbot',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one({'sign': 'callbot'}).get('username')
    token = CALL_BOT_Controllers.get_callbot_token()

    payload = json.dumps({
        "hotline": hotline,
        "called": called,
        "bot_id": bot_id,
        "bot_region": bot_region,
        "call_params": call_params[0],
        "cus_id": cus_id,
        "request_id": str(secrets.token_urlsafe(8)),
        "url_webhook": General_control.get_url_webhook(current_user.get('_id')),
        "is_asr": General_control.check_have_asr(current_user.get('_id'))
    })
    headers = {
        'client-id': username,
        'x-access-token': token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    insert_data = {"user_id": current_user.get('_id'),
                   "username": current_user.get('name'),
                   "service": "callbot",
                   "timestamp": General_control.getNOW(),
                   "link_api": url,
                   "request": payload,
                   "response": response.json()
                   }
    if current_user.get('name') == "SHB":
        mydb.shb.insert_one(insert_data)
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callbot',
                     General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
        return (response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callbot',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)

    return (response.json())

@CALL_BOT.get('/call/bot/get', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def callbot_bot_get(current_user: Schemas_share.User = Depends(get_current_active_user)):
    url = CALL_BOT_Controllers.get_link_function_callbot('callbot_bot_get')
    url_gw = setting.BASE_URL + "/call/bot/get"
    service_id = str(mydb.services.find_one({'sign': 'callbot'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            'msg': 'Too limit'
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'callbot',
                     General_control.getNOW(), url, '', client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    username = mydb.services.find_one(
        {'sign': 'callbot'}).get('username')
    token = CALL_BOT_Controllers.get_callbot_token()

    payload = {}
    headers = {
        'client-id': username,
        'x-access-token': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    General_control.save_log(current_user.get('_id'), current_user.get('name'),
                 'callbot', General_control.getNOW(), url, '', response.json(), '', response.json(), url_gw)

    return (response.json())
