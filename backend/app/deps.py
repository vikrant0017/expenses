from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from app.utils import jwt_decode

# extracts the scheme and token
oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")  # tokenUrl - For the OpenAPI docs


def get_current_user(token: Annotated[str, Depends(oauth2scheme)]) -> int:
    # The token is some secret we need to decode and get the user
    json = jwt_decode(token)

    if not json.get("user_id"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
            headers={"WWW-Authenticate": "Bearer"},  # OAuth Spec
        )

    return json.get("user_id")
