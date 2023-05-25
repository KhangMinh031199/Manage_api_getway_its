from ctypes import c_uint

from Manage.Management_APIs.Schemas import Schemas_share, Schemas_share
from fastapi import Depends, Query, Form, APIRouter, HTTPException, status
from Manage.Authentication.Token import get_current_active_user
from typing import Optional
from bson.objectid import ObjectId
from Manage.mongo_connect import mongo_create
import pymongo
from Manage.Management_APIs.Controller_APIs import USER_Controllers, General_control
import secrets
from Manage.Authentication.Hash_Password import Hash
from Manage.Management_APIs.Schemas import Schemas_share
import bson

mydb =  mongo_create()

USER=APIRouter(tags=['User'])

#test tren postman chua co
@USER.get("/user/info")
async def info_current_user(current_user: Schemas_share.User = Depends(get_current_active_user)):
    return current_user

@USER.get("/user/log")
async def log_current_user(callbot_id: Optional[str] = None, page_size: int = Query(None, ge=1), page: int = Query(None, ge=1), current_user: Schemas_share.User = Depends(get_current_active_user)):
    client_id = current_user.get("_id")
    if callbot_id:
        filter = {"user_id": ObjectId(
            client_id), "request.callbot_id": callbot_id}
    else:
        filter = {"user_id": ObjectId(client_id)}

    if not page_size:
        page_size = 10**6
    if not page:
        page = 1
    if page_size < 1 or page_size < 1:
        return {'status': 0, 'msg': 'page_size không hợp lệ'}

    log = mydb.api_logs.find(filter, {"origin_request": 0, "origin_response": 0}).sort("timestamp", pymongo.DESCENDING).skip(page_size * (page - 1)) \
        .limit(page_size)

    return {"data": list(log), "total": log.count(), 'status': 1}


@USER.get("/user/services")
async def info_registered_service(current_user: Schemas_share.User = Depends(get_current_active_user)):
    print("======", current_user.get('_id'))
    return USER_Controllers.get_service_registered(current_user.get('_id'))

@USER.get("/user/get_full_services")
async def get_full_services(current_user: Schemas_share.User = Depends(get_current_active_user)):
    return USER_Controllers.get_services()

#in conllection client
@USER.post("/user/create")
async def user_create(name: str = Form(...), email: str = Form(...), phone: str = Form(...)):
    #tao khoa bi mat api_key do dai 27 byte bang thu vien secrets (Base64)
    api_key = secrets.token_urlsafe(27)
    services = []
    insert_data = {
        'name': name,
        'avatar': '/static/img/undraw_profile.svg',
        'email': email,
        'password': Hash.get_password_hash("Demo@123"),
        'phone': phone,
        'partner_id': '',
        'active': 1,
        'api_key': api_key,
        'services': services,
        'created_at': General_control.getNOW()
    }

    x = mydb.clients.insert_one(insert_data)
    response = {
        "message": "Thêm thành công",
        "data": {
            "_id": str(x.inserted_id),
            "name": name,
            "api_key": api_key
        }
    }
    return response

#Dang ky dich vu cho user
@USER.post("/user/register_service")
async def register_one_service(client_id: str = Form(...), service_id: str = Form(...), limit_request: int = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    insert_data = {
        'service_id': service_id,
        'limit_request': limit_request,
        'remaining_request': limit_request,
        'register_date':General_control.getNOW()
    }
    if not bson.objectid.ObjectId.is_valid(client_id) or not bson.objectid.ObjectId.is_valid(service_id):
        response = {
            "message": "Sai định dạng ID"
        }
        return response
    exist_client = mydb.clients.find_one({'_id': ObjectId(client_id)})
    if not exist_client:
        response = {
            "message": "Không tồn tại khách hàng"
        }
        return response
    exist_service = mydb.services.find_one({'_id': ObjectId(service_id)})
    if not exist_service:
        response = {
            "message": "Không tồn tại dịch vụ"
        }
        return response
    is_exist = mydb.clients.find_one(
        {'_id': ObjectId(client_id), 'services.service_id': service_id})
    if is_exist:
        response = {
            "message": "Dịch vụ đã đăng ký"
        }
        return response
    mydb.clients.find_one_and_update(
        {"_id": ObjectId(client_id)},
        {'$push': {
            "services": insert_data
        }
        }
    )
    mydb.clients.find_one(
        {'_id': ObjectId(client_id), 'services.service_id': service_id})
    response = {
        "message": "Thêm thành công",
        "data": insert_data
    }
    return response

@USER.delete("/user/remove_service_registered")
async def remove_service_registered(client_id: str = Form(...), service_id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    if not bson.objectid.ObjectId.is_valid(client_id) or not bson.objectid.ObjectId.is_valid(service_id):
        response = {
            "message": "Sai định dạng ID"
        }
        return response
    exist_client = mydb.clients.find_one({'_id': ObjectId(client_id)})
    if not exist_client:
        response = {
            "message": "Không tồn tại khách hàng"
        }
        return response
    exist_service = mydb.services.find_one({'_id': ObjectId(service_id)})
    if not exist_service:
        response = {
            "message": "Không tồn tại dịch vụ"
        }
        return response
    is_exist = mydb.clients.find_one(
        {'_id': ObjectId(client_id), 'services.service_id': service_id})
    if not is_exist:
        response = {
            "message": "Dịch vụ chưa đăng ký"
        }
        return response
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    mydb.clients.update_one({"_id": client_id}, {
                            "$pull": {"services": {"service_id": service_id}}})
    response = {
        "message": "Xoá thành công"
    }
    return response


@USER.post("/user/get_service_registered")
async def get_service_registered_post(client_id: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    find_client = mydb.clients.find_one({"_id": client_id})
    if find_client is None:
        return []
    register_services = find_client.get('services')
    services = []
    for x in register_services:
        service = {}
        service['name'] = (USER_Controllers.get_service_info(x['service_id'])).get('name')
        if service is None:
            continue
        service['register_date'] = x["register_date"]
        service['limit_request'] = x['limit_request']
        service['remaining_request'] = x['remaining_request']
        services.append(service)
    return services

### Đổi pass
@USER.post("/user/change_password")
async def change_password(old_password: str = Form(...), new_password: str = Form(..., min_length=8, max_length=16), new_password_again:str = Form(..., min_length=8, max_length=16),
                          current_user: Schemas_share.User = Depends(get_current_active_user)):
    if not Hash.verify_password(old_password, current_user['password']):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The old password is incorrect!")
    else:
        if new_password != new_password_again:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The new password is't same")
        else:
            if USER_Controllers.check_password(new_password) is False:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your password must be 8-16 characters, and include at least one lowercase letter, one uppercase letter,a number and a special character!")
            else:
                new_pass=Hash.get_password_hash(new_password)
                mydb.clients.update_one({'_id': current_user['_id']},{"$set": {'password': new_pass}})
                return HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Change password have successfuly!!!")