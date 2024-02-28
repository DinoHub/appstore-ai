import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.accesscontrol import (
    AccessControlResponse
)

from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from ..config.config import config

keycloak_connection = KeycloakOpenIDConnection(
                        server_url=config.KEYCLOAK_SERVER_URL,
                        # username='',
                        # password='',
                        realm_name=config.KEYCLOAK_REALM_NAME,
                        # user_realm_name= config.KEYCLOAK_REALM_NAME,
                        client_id=config.KEYCLOAK_CLIENT_ID,
                        client_secret_key=config.KEYCLOAK_CLIENT_SECRET_KEY,
                        verify=True
                        )

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

router = APIRouter(prefix="/access-control", tags=["Access control"])

@router.post("/", response_model=AccessControlResponse)
def validate_usernames(
    usernamesList: List[str],
) -> Dict:
    """Validate usernames.

    Args:
        usernamesList (List of str): usernames
    Raises:
        HTTPException: 500 Internal Server Error if error occurs

    Returns:
        Dict: Validation results
    """
    validUsernames = []
    invalidUsernames = []
    try:
        users_in_keycloak = keycloak_admin.get_users({})
        usernames_in_keycloak_set = {user['username'] for user in users_in_keycloak}
        for username in usernamesList:
            if username in usernames_in_keycloak_set:
                validUsernames.append(username)
            else:
                invalidUsernames.append(username)
        newUsernamesList = [username for username in usernamesList if username not in invalidUsernames]
        data = {"validUsernames": validUsernames, 
                "invalidUsernames": invalidUsernames,
                "newUsernamesList": newUsernamesList
        }
        return data

    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating usernames.",
        ) from err


