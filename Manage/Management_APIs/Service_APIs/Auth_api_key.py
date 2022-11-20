from fastapi import APIRouter, Form, HTTPException, status
from Manage.Management_APIs.Schemas.Schemas_auth import Token
from Manage.Management_APIs.Controller_APIs.Auth_api_key_Controllers import get_user
from datetime import timedelta
from Manage.Authentication.Token import create_access_token
from Manage.Management_APIs.Controller_APIs import General_control
from Manage import setting

auth=APIRouter(tags=['Authentication'])

@auth.post("/auth", response_model=Token)
async def login(api_key: str = Form(...)):
    user = get_user(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Incorrect api key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['api_key']}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "time_expired": General_control.getNOW() + 7200}