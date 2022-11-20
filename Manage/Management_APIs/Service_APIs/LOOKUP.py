from fastapi import APIRouter, Form, Depends
from pydantic.schema import Generic

from Manage.Authentication.Token import get_current_active_user
from Manage.mongo_connect import mydb
from fastapi_limiter.depends import RateLimiter
from Manage.Management_APIs.Controller_APIs import LOOKUP_Controllers, General_control
import requests
import json
from Manage.Management_APIs.Schemas import Schemas_share
from Manage import setting

LOOKUP=APIRouter(tags=['LookUp'])

@LOOKUP.post("/lookup/basic_personal_information", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_basic_personal_information(msisdn: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):

    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token(client_id, secret_key, request_id, msisdn)
    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/basic_personal_information?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}"
    url_gw = setting.BASE_URL + "/lookup/basic_personal_information"
    client_request = {
        'msisdn': msisdn
    }

    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }

    name_service = 'basic_personal_information'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), client_request, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())


####
@LOOKUP.post("/lookup/call_history", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_call_history(msisdn: str = Form(...), n: int = Form(...), cp1: str = Form(...), cp2: str = Form(...),
                              cp3: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    if n < 1 or n > 20:
        n = 10
    secret_token = LOOKUP_Controllers.get_secret_token_vs2(client_id,secret_key,request_id,msisdn,n,cp1,cp2,cp3)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/v/call_history?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}&n={n}&cp1={cp1}&cp2={cp2}&cp3={cp3}"
    url_gw = setting.BASE_URL + "/lookup/call_history"
    client_request = {
        'msisdn': msisdn,
        'n': n,
        'cp1': cp1,
        'cp2': cp2,
        'cp3': cp3
    }

    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))

    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False or LOOKUP_Controllers.validation_check_lookup_phone(cp1) is False or LOOKUP_Controllers.validation_check_lookup_phone(cp2) is False or LOOKUP_Controllers.validation_check_lookup_phone(cp3) is False:
        client_response = {
            'status_code': 0,
            "msg": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"
        }
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }
    payload.update({'n': n, 'cp1': cp1, 'cp2': cp2, 'cp3': cp3})
    name_service = 'call_history'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())
###

@LOOKUP.post("/lookup/address", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_address(msisdn: str = Form(...), accuracy_of_address: str = Form(...), n: int = Form(...),
                         current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    if n < 1 or n > 10:
        n = 5
    secret_token = LOOKUP_Controllers.get_secret_token_vs3(client_id,secret_key,request_id,msisdn,accuracy_of_address,n)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/v/address?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}&accuracy_of_address={accuracy_of_address}&n={n}"
    url_gw = setting.BASE_URL + "/lookup/address"
    client_request = {
        'msisdn': msisdn,
        'accuracy_of_address': accuracy_of_address,
        'n': n
    }
    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "message": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if accuracy_of_address not in ['P', 'D', 'V']:
        client_response = {
            'status_code': 0,
            "msg": "Độ sâu của địa chỉ không đúng định dạng. Có các giá trị: P: Tỉnh/Thành Phố -- D: Quận/Huyện -- V: Xã/Phường"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }
    payload.update({"accuracy_of_address": accuracy_of_address, "n": n})
    name_service = 'address'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())


@LOOKUP.post("/lookup/get_fullname_dob", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_get_fullname_dob(msisdn: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token(client_id, secret_key, request_id, msisdn)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/ci01?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}"
    url_gw = setting.BASE_URL + "/lookup/get_fullname_dob"
    client_request = {
        'msisdn': msisdn
    }
    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "message": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }

    name_service = 'get_fullname_dob'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())

####
@LOOKUP.post("/lookup/get_identity_card_number", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_get_identity_card_number(msisdn: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token(client_id, secret_key, request_id, msisdn)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/ci07?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}"
    url_gw = setting.BASE_URL + "/lookup/get_identity_card_number"
    client_request = {
        'msisdn': msisdn
    }

    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "message": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }

    name_service = 'get_identity_card_number'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())


@LOOKUP.post("/lookup/person_info_collect", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_person_info_collect(msisdn: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token(client_id, secret_key, request_id, msisdn)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/person_info_collect?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}"
    url_gw = setting.BASE_URL + "/lookup/person_info_collect"
    client_request = {
        'msisdn': msisdn
    }
    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "message": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }

    name_service = 'person_info_collect'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())



@LOOKUP.post("/lookup/idphonen", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_idphonen(msisdn: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token(client_id, secret_key, request_id, msisdn)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/idphonen?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&msisdn={msisdn}"
    url_gw = setting.BASE_URL + "/lookup/idphonen"
    client_request = {
        'msisdn': msisdn
    }
    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))
    if LOOKUP_Controllers.validation_check_lookup_phone(msisdn) is False:
        client_response = {
            'status_code': 0,
            "message": "Sai định dạng số điện thoại. Số điện thoại có định dạng: 84xxxxxxxxx"}
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    General_control.decrease_remaining_request(current_user.get('_id'), service_id)
    payload = {}
    headers = {
    }

    name_service = 'idphonen'
    result_check = LOOKUP_Controllers.check_in_db(msisdn, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(msisdn, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            msisdn, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            msisdn, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())

# Truy vấn số điện thoại của customer thông qua số chứng minh thư nhân dân của customer

@LOOKUP.post("/lookup/get_list_msisdn", dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def lookup_get_list_msisdn(nic_no: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = mydb.services.find_one({'sign': 'lookup'}).get('username')
    secret_key = mydb.services.find_one({'sign': 'lookup'}).get('password')
    request_id = LOOKUP_Controllers.get_request_id_lookup()
    secret_token = LOOKUP_Controllers.get_secret_token_vs4(client_id,secret_key,request_id,nic_no)

    url = f"https://api.fintrust.store/p/v1.5/iqvs/q/idpx?client_id={client_id}&secret_token={secret_token}&request_id={request_id}&nic_no={nic_no}"
    url_gw = setting.BASE_URL + "/lookup/get_list_msisdn"
    client_request = {
        'nic_no': nic_no
    }
    service_id = str(mydb.services.find_one({'sign': 'lookup'}).get('_id'))

    if General_control.get_remaining_request(current_user.get('_id'), service_id) == 0:
        client_response = {
            'status_code': 100,
            "msg": "Too limit"
        }
        General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                     General_control.getNOW(), url, client_request, client_response, '', '', url_gw)
        return client_response
    payload = {}
    headers = {
    }

    name_service = 'get_list_msisdn'
    result_check = LOOKUP_Controllers.check_in_db(nic_no, name_service, payload)
    if type(result_check) != str:
        response = result_check.get('response')
        General_control.save_log(current_user.get('_id'), current_user.get(
            'name'), 'lookup', General_control.getNOW(), url, payload, response, '', '', url_gw)
        return result_check.get('response')
    response = requests.request("GET", url, headers=headers, data=payload)
    if result_check == 'push_service':
        LOOKUP_Controllers.user_lookup_push_service(nic_no, name_service,
                                     payload, response.json())
    elif result_check == 'update':
        LOOKUP_Controllers.user_lookup_update_service(
            nic_no, name_service, payload, response.json())
    else:  # Create user
        LOOKUP_Controllers.user_lookup_create_user(
            nic_no, name_service, payload, response.json())

    General_control.save_log(current_user.get('_id'), current_user.get('name'), 'lookup',
                 General_control.getNOW(), url, client_request, response.json(), payload, response.json(), url_gw)
    LOOKUP_Controllers.update_request_id_lookup()
    return (response.json())

