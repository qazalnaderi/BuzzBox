from http.client import HTTPException
from fastapi import HTTPException, status
import jwt
from fastapi import status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
import logging 
SECRET_KEY = "3ffdda4a51a141cff4485a36f9cd137287f2526c1edb8300cd678ab96a49d1bd"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire.timestamp(),  
            "email": data.get("email"), 
            "user_id": data.get("user_id") 
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        return JSONResponse(status_code=500, content={"message": f"Token creation failed: {str(e)}"})


def verify_access_token(token: str):
    logging.info(f"Received token: {token}")
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=["HS256"])
        logging.info(f"Decoded payload: {payload}")
        logging.info(payload.get("user_id"))
        return payload
    except jwt.ExpiredSignatureError:
        logging.info("Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired")
    except jwt.JWTError:
        logging.info("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error during token verification: {str(e)}")
