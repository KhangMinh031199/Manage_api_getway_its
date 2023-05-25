from fastapi import Form
from typing import List
import json
from Manage.mongo_connect import mongo_create
import secrets
import requests
from bson.objectid import ObjectId

mydb=mongo_create()
def call_param_dict(call_params: List[str] = Form(...)):
    try:
        return list(map(json.loads, call_params))
    except:
        return []

def get_link_function_callbot(apifunction):
    callbot = mydb.services.find_one({"sign": "callbot"})
    for x in callbot.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

def get_callbot_token():
    url = get_link_function_callbot('get_callbot_token')

    username = mydb.services.find_one(
        {'sign': 'callbot'}).get('username')
    password = mydb.services.find_one(
        {'sign': 'callbot'}).get('password')
    payload = json.dumps({
        "request_id": str(secrets.token_urlsafe(8)),
        "username": username,
        "password": password,
        "partyCode": username
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return (response.json().get('data').get('token'))

def get_url_webhook(client_id):
    url = mydb.clients.find_one(
        {'_id': ObjectId(client_id)}).get('url_webhook')
    if url is None:
        return ""
    return url