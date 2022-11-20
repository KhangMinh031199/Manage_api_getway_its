import sys

ITEMS_PER_PAGE = 10
OTP_EXPIRE_SECONDS = 300
#MONGODB_HOST = 'mongo'
MONGODB_HOST='localhost'
MONGODB_PORT = 27017
#MONGODB_NAME = 'api_platform'
MONGODB_NAME='api_getway'

CELERY_URL = 'redis://redis/6'
FASTAPI_REDIS_URL = 'redis://redis/5'

#MONGODB_USER = 'admin'
MONGODB_USER = 'khangminh123'
#MONGODB_PASSWORD = 'BAckSpdaEaMLtSRPSl_now'
MONGODB_PASSWORD = '1234567890p'

HOST = "0.0.0.0"

# CMC
#MONGODB_USER_CMC = 'smartbot'
#MONGODB_PASSWORD_CMC = 'ahmFwdevvk6g6Hw'
#MONGODB_HOST_CMC = '103.229.42.121'

ELASTICSEARCH_SERVER = '125.212.225.71'
ELASTICSEARCH_USER = 'elastic'
ELASTICSEARCH_PASSWORD = '@aicungbiet@'

if 'local' in sys.argv:

    FASTAPI_REDIS_URL = 'redis://127.0.0.1:6379/5'
    #MONGODB_HOST = '127.0.0.1'
    MONGODB_HOST = 'localhost'
    CELERY_URL = 'redis://127.0.0.1:6379/10'
    HOST = "127.0.0.1"

# Thông tin các hằng số sử dụng

ACCESS_TOKEN_EXPIRE_MINUTES = 120

#key và thuật toán để hash password
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# số lượng request đến api trong vòng 60s. BASE_URL là domain đang chạy của chương trình
RATE_LIMITING_TIMES = 50
RATE_LIMITING_SECONDS = 60
BASE_URL = "https://api.smartbot.vn/"
