from Manage.mongo_connect import mongo_create
import json
import requests

mydb=mongo_create()
def get_link_function_ocr(apifunction):
    ocr = mydb.services.find_one({"sign": "ocr"})
    for x in ocr.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')

def get_token_ocr():
    url = get_link_function_ocr('ocr_auth')

    client_id = mydb.services.find_one({'sign': 'ocr'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'ocr'}).get('password')
    payload = json.dumps({
        "client_id": client_id,
        "secret_key": secret_key
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.json().get('data'):
        return(response.json().get('data'))
    return ""

### mới 24/04/2023 vs3
def get_authorization_ocr_v3():
    username = mydb.services.find_one({'sign': 'ocr_v3'}).get('username')
    password = mydb.services.find_one({'sign': 'ocr_v3'}).get('password')

    return username, password