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
    usernames_list: List[str],
) -> Dict:
    """Validate usernames.

    Args:
        usernames_list (List of str): usernames
    Raises:
        HTTPException: 500 Internal Server Error if error occurs

    Returns:
        Dict: Validation results
    """
    valid_usernames = []
    invalid_usernames = []
    try:
        users_in_keycloak = keycloak_admin.get_users({})
        usernames_in_keycloak_set = {user['username'] for user in users_in_keycloak}
        for username in usernames_list:
            if username in usernames_in_keycloak_set:
                valid_usernames.append(username)
            else:
                invalid_usernames.append(username)
        new_usernames_list = [username for username in usernames_list if username not in invalid_usernames]
        data = {"validUsernames": valid_usernames, 
                "invalidUsernames": invalid_usernames,
                "newUsernamesList": new_usernames_list
        }
        return data

    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating usernames.",
        ) from err


