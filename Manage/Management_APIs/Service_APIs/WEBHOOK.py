from fastapi import APIRouter, Depends, Form
from fastapi_limiter.depends import RateLimiter
from Manage.Authentication.Token import get_current_active_user
from Manage.mongo_connect import mongo_create
from bson.objectid import ObjectId
from Manage.Management_APIs.Schemas import Schemas_share
from Manage import setting

mydb=mongo_create()
WEBHOOK=APIRouter(tags=["Webhook"])

@WEBHOOK.post('/register_webhook', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def register_webhook(url: str = Form(...), current_user: Schemas_share.User = Depends(get_current_active_user)):
    is_exist = mydb.clients.find_one({'url_webhook': url})
    if is_exist:
        return {"message": "URL đã tồn tại"}
    mydb.clients.update_one(
        {'_id': ObjectId(current_user.get('_id'))}, {"$set": {'url_webhook': url}})