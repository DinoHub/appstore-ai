import Keycloak from "keycloak-js";

const CLIENT_ID = "";
const KEYCLOAK_URL = "";
const KEYCLOAK_REALM = "";

const initOptions = {
    realm: KEYCLOAK_REALM,
    url: KEYCLOAK_URL,
    "ssl-required": "external",
    clientId: CLIENT_ID,
    "public-client": true,
    "confidential-port": 0,
}

// If token expires within minTokenValidityInSeconds, the token is refreshed. 
// If minTokenValidityInSeconds is assigned to -1, the token will be forcibly refreshed.
const minTokenValidityInSeconds = -1;

const keycloakInstance = new Keycloak(initOptions);

/**
 * Initializes Keycloak instance and calls the provided callback function if successfully authenticated.
 *
 * @param onAuthenticatedCallback
 */
const Login = () => {
    const isAuthenticated = keycloakInstance.init({onLoad: "login-required"});
    return isAuthenticated
};

const UserId = (): string | undefined =>
    keycloakInstance?.tokenParsed?.sub;

const UserName = (): string | undefined =>
    keycloakInstance?.tokenParsed?.preferred_username;

const FullName = (): string | undefined =>
    keycloakInstance?.tokenParsed?.name;

const Token = (): string | undefined => keycloakInstance?.token;

const Logout = () => keycloakInstance.logout();

const RefreshToken = async () => {
    try {
        const isTokenUpdated =  await keycloakInstance.updateToken(minTokenValidityInSeconds)
        return isTokenUpdated
    } catch (err) {
        console.error("Failed to refresh token!");
    }
}

const UserRoles = (): string[] | undefined => {
    if (keycloakInstance.resourceAccess == undefined) {
        return undefined;
    }
    return keycloakInstance.resourceAccess[CLIENT_ID].roles;
}

const isLoggedIn = () => !!keycloakInstance.token;

const KeyCloakService = {
    CallLogin: Login,
    GetUserId: UserId,
    GetUserName: UserName,
    GetFullName: FullName,
    GetAccessToken: Token,
    CallLogOut: Logout,
    GetUserRoles: UserRoles,
    CallIsLoggedIn: isLoggedIn,
    CallRefreshToken: RefreshToken
};

export default KeyCloakService;