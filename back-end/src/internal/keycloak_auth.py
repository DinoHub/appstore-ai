from fastapi import Depends, HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError, jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import Json
from keycloak import KeycloakOpenID
from passlib.context import CryptContext

from ..config.config import config
from ..models.iam import TokenData, UserRoles

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection


# Create a KeycloakOpenID instance for the Bearer-only client
keycloak_bearer_only = KeycloakOpenID(
    server_url= config.KEYCLOAK_SERVER_URL, 
    realm_name= config.KEYCLOAK_REALM_NAME,
    client_id= config.KEYCLOAK_CLIENT_ID,
    client_secret_key= config.KEYCLOAK_CLIENT_SECRET_KEY,
    verify=True
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl= config.KEYCLOAK_AUTHORIZATION_URL,
    tokenUrl= config.KEYCLOAK_TOKEN_URL
)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    # headers={"WWW-Authenticate": "Bearer"}, # Do we need to send headers?
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_idp_public_key():
    '''
    Obtain the public key of the keycloak
    '''
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_bearer_only.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )

async def get_tokendata(identity: Json) -> TokenData:
    role_list = identity['resource_access']['ai-appstore-frontend']['roles']
    return TokenData(
        user_id=identity.get('sub'),
        name=identity.get('name'),
        role=role_list[0],
        # role="admin", # TODO: remove hardcoded role
        exp=identity.get('exp'),
    )



async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    """Get current user from JWT token

    Args:
        token (str, optional): Encoded JWT. Defaults to Depends(oauth2_scheme).

    Raises:
        CREDENTIALS_EXCEPTION: If token does not provide a user or role
        HTTPException: If token is expired
        CREDENTIALS_EXCEPTION: If token is invalid or CSRF token is invalid
        HTTPException: If token does not reference a valid user

    Returns:
        TokenData: _description_
    """
    identity = {}
    try:
        identity = keycloak_bearer_only.decode_token(token, key=await get_idp_public_key())
        token_data = await get_tokendata(identity)
        # But userid and role will never be empty unless user did not sign up properly.
        if token_data.user_id is None or token_data.role is None: 
            raise CREDENTIALS_EXCEPTION
            
    # Think of the cases that will trigger this
    except ExpiredSignatureError as err: # this will never happen as we keep refreshing token?
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Token Expired",
        ) from err
    except (JWTError) as err: # base error for JWT
        raise CREDENTIALS_EXCEPTION from err
    
    return token_data

async def initialize_keycloak_admin() -> KeycloakAdmin:
    keycloak_connection = KeycloakOpenIDConnection(
        server_url=config.KEYCLOAK_SERVER_URL,
        realm_name=config.KEYCLOAK_REALM_NAME,
        client_id=config.KEYCLOAK_CLIENT_ID,
        client_secret_key=config.KEYCLOAK_CLIENT_SECRET_KEY,
        verify=True
    )
    return KeycloakAdmin(connection=keycloak_connection)

async def check_is_admin(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    """Validate that user is an admin

    Args:
        request (Request): Incoming HTTP request
        token (str, optional): Encoded JWT. Defaults to Depends(oauth2_scheme).
        csrf (CsrfProtect, optional): CSRF Protection. Defaults to Depends().

    Raises:
        HTTPException: If user is not an admin

    Returns:
        TokenData: Pydantic data model of user
    """
    user = await get_current_user(token)
    if user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin access",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user