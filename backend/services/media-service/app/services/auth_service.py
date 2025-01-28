from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from loguru import logger
from app.infrastructure.clients.iam_client import IAMClient
from app.domain.schemas.token_schema import TokenDataSchema
from app.core.config.config import get_settings
from typing import Annotated
from loguru import logger
from fastapi import Depends
from app.services import user_manager
from pydantic import ValidationError


config = get_settings()



config = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"http://iam.localhost:9000/login/user/login",
    scheme_name="UserOAuth2"
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    client: Annotated[IAMClient, Depends()],
) -> TokenDataSchema:
    """
    Retrieve the current user based on the provided token.

    Args:
        token (str): The JWT token extracted from the request.
        client (IAMClient): The client to validate the token and fetch user data.

    Returns:
        TokenDataSchema: The decoded user data schema.
    """
    if not token:
        logger.error("No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        logger.info(f"Validating token: {token}")
        user_data = await client.validate_token(token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        logger.info(f"Token validated. User: {user_data.email_address}")
        return user_data

    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token validation",
        )
