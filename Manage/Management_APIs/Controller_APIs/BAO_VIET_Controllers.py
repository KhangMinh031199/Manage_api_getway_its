import requests
from Manage import mongo_connect
from Manage import setting
from Manage.Management_APIs.Controller_APIs import General_control
import json
mydb = mongo_connect.mongo_create()

def baoviet_get_api_token():
    filter = {'sign': 'bao_viet'}
    api_function = 'baoviet_auth'
    sign_name = 'bao_viet'
    url = General_control.get_link_function_service(api_function,sign_name)

    #get user, password
    username = mydb.services.find_one(filter).get('username')
    password = mydb.services.find_one(filter).get('password')
    payload = json.dumps({
        "username": username,
        "password": password
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url=url, headers=headers, data=payload)

    return (response.json())['id_token']