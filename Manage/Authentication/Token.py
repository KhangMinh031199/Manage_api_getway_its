from typing import Dict, Optional, Any, Type, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Body, Depends, FastAPI, HTTPException, status, File, Form, UploadFile, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import Schemas_Authentication
from Manage.mongo_connect import mydb
from Manage.Management_APIs.Schemas import Schemas_share
from Manage import setting

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "status_code": 401,
            "msg": "Could not validate credentials"
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = Schemas_Authentication.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = mydb.clients.find_one({'api_key': token_data.username})
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Schemas_share.User = Depends(get_current_user)):
    if current_user["active"]:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")
