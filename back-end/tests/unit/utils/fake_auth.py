from src.models.iam import TokenData, UserRoles


def fake_login_user() -> TokenData:
    return TokenData(user_id="test_1", name="Test User", role=UserRoles.user)


def fake_login_admin() -> TokenData:
    return TokenData(user_id="test_2", name="Test Admin", role=UserRoles.admin)
