from Manage.mongo_connect import mydb
import secrets
import requests
import json
from bson import ObjectId
from Manage.Management_APIs.Controller_APIs import General_control

def get_link_function_callagent(apifunction):
    callagent = mydb.services.find_one({"sign": "callagent"})
    for x in callagent.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

def get_callagent_token():
    #url = General_control.get_link_function_service('get_callagent_token','callagent')
    url = General_control.get_link_function_service('get_token_callagent',"callagent")
    print(url)
    url="http://125.212.225.71:8344/smartseller/auth/login"

    username = mydb.services.find_one(
        {'sign': 'callagent'}).get('username')
    password = mydb.services.find_one(
        {'sign': 'callagent'}).get('password')
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
    print("==================")

    return (response.json().get('data').get('token'))



