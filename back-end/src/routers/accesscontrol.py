import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.accesscontrol import (
    AccessControlResponse
)

from ..internal.keycloak_auth import initialize_keycloak_admin
from ..config.config import config

router = APIRouter(prefix="/access-control", tags=["Access control"])

@router.post("/", response_model=AccessControlResponse)
async def validate_usernames(
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
    try:
        keycloak_admin = await initialize_keycloak_admin()
        users_in_keycloak = keycloak_admin.get_users({})
        usernames_in_keycloak_set = {user['username'] for user in users_in_keycloak}
        valid_usernames = list(filter(lambda username: username in usernames_in_keycloak_set, usernames_list))
        invalid_usernames = list(filter(lambda username: username not in usernames_in_keycloak_set, usernames_list))
        new_usernames_list = list(filter(lambda username: username not in invalid_usernames, usernames_list))
        data = {
            "validUsernames": valid_usernames, 
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


