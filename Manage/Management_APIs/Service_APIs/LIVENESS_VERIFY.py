from fastapi import HTTPException, APIRouter, Form, Depends
from fastapi_limiter.depends import RateLimiter
from Manage import setting
from Manage.Management_APIs.Schemas.Schemas_share import User
from Manage.Authentication.Token import get_current_active_user
from Manage.Management_APIs.Controller_APIs import LIVENESS_VERIFY_Controllers, General_control
import requests
import logging
import traceback
from Manage.mongo_connect import mongo_create

mydb = mongo_create()
LIVENESS_VERIFY = APIRouter(tags=['Liveness Verify'])

@LIVENESS_VERIFY.get('/v2/ekyc/url/verify_liveness', dependencies=[Depends(RateLimiter(times=setting.RATE_LIMITING_TIMES, seconds=setting.RATE_LIMITING_SECONDS))])
async def ekyc_url_verify_liveness_v2 (portrait_left: str, portrait_mid: str, portrait_right: str):
    try:
        url = General_control.get_link_function_service('ekyc_url_verify_liveness_v2','liveness_verify_v2')
        url_gw = setting.BASE_URL + 'v2/ekyc/url/verify_liveness'
        client_request = {
            'portrait_right': portrait_right,
            'portrait_left': portrait_left,
            'portrait_mid': portrait_mid
        }

        service_id = str(mydb.services.find_one({'sign':'liveness_verify_v2'}).get('_id'))

    except:
        logging.info('LIVENESS VERIFY URL - ERROR: {}'.format(traceback.format_exc()))
        return HTTPException(status_code=500, detail='LIVENESS VERIFY URL - Internal Service Error!')

