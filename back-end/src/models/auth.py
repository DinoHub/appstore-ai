"""Data models for authentication."""
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel

from ..config.config import config


class CsrfSettings(BaseModel):
    """Cross-site request forgery protection config"""

    secret_key: str = config.SECRET_KEY
    cookie_secure: bool = config.SECURE_COOKIES


# NOTE: Should this be moved to internal/auth.py?
class OAuth2PasswordBearerWithCookie(OAuth2):
    """Custom OAuth2PasswordBearer class to allow cookie authentication"""

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = True,
    ):
        """Custom OAuth2PasswordBearer class to allow cookie authentication

        Args:
            tokenUrl (str): Auth token URL
            scheme_name (Optional[str], optional): OAuth2 Scheme. Defaults to None.
            scopes (Optional[dict], optional): OAuth2 scopes. Defaults to None.
            auto_error (bool, optional): If should throw exception on failure. Defaults to True.
        """
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password=OAuthFlowPassword(tokenUrl=tokenUrl, scopes=scopes)
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        """Intercept request and check for access token in cookie
        to validate user

        Args:
            request (Request): Incoming HTTP request

        Raises:
            HTTPException: If no authorization header is found

        Returns:
            Optional[str]: Encoded JWT
        """
        authorization: Optional[str] = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization or "")

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param
