from fastapi import FastAPI
import uvicorn
from Manage import setting
from Manage.Management_APIs.Service_APIs.USER import USER
from Manage.Management_APIs.Service_APIs.Auth_api_key import auth
from Manage.Management_APIs.Service_APIs.VOICE_ID import VoiceID
from Manage.mongo_connect import mongo_create
import aioredis  # fastapi-limit
from fastapi_limiter import FastAPILimiter
from Manage.Management_APIs.Service_APIs.ASR import ASR
from Manage.Management_APIs.Service_APIs.FACE_ID import FaceID
from Manage.Management_APIs.Service_APIs.OCR import OCR
from Manage.Management_APIs.Service_APIs.LOOKUP import LOOKUP
from Manage.Management_APIs.Service_APIs.CALL_AGENT import CALL_AGENT
from Manage.Management_APIs.Service_APIs.CALL_BOT import CALL_BOT
from Manage.Management_APIs.Service_APIs.IDENTIFICATION import IDENTIFICATION
from Manage.Management_APIs.Service_APIs.WEBHOOK import WEBHOOK
from Manage.Management_APIs.Service_APIs.TTS import TTS
from Manage.Management_APIs.Service_APIs.VOICE_BIO import VOICE_BIO
from Manage.Management_APIs.Service_APIs.OCR_V3 import OCR_V3
from Manage.Management_APIs.Service_APIs.BAO_VIET import BAO_VIET
from Manage.Management_APIs.Service_APIs.RAR import RAR
from Manage.Management_APIs.Service_APIs.FACE_MATCHING import FACE_MATCHING
from Manage.Management_APIs.Service_APIs.VOICE_BIO_V2 import VOICE_BIO_V2
from Manage.Management_APIs.Service_APIs.LIVENESS_VERIFY import LIVENESS_VERIFY

mydb=mongo_create()

app=FastAPI()

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool(setting.FASTAPI_REDIS_URL)
    await FastAPILimiter.init(redis)

app.include_router(USER)
app.include_router(auth)
app.include_router(VoiceID)
app.include_router(ASR)
app.include_router(FaceID)
app.include_router(OCR)
app.include_router(OCR_V3)
app.include_router(LOOKUP)
##Call agent với call bot là phần cũ nên không chạy được nữa, phần này chỉ copy từ file api_getway cho đầy đủ mã nguồn
app.include_router(CALL_AGENT)
app.include_router(CALL_BOT)

app.include_router(IDENTIFICATION)
app.include_router(WEBHOOK)
app.include_router(VOICE_BIO)
app.include_router(TTS)
app.include_router(BAO_VIET)
app.include_router(RAR)
app.include_router(FACE_MATCHING)
app.include_router(VOICE_BIO_V2)
app.include_router(LIVENESS_VERIFY)

if __name__ == "__main__":
    uvicorn.run("main:app", host=setting.HOST, port=8000, reload=True)