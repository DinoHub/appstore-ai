from src.models.iam import TokenData, UserRoles


def fake_login_user() -> dict:
    return TokenData(user_id="test_1", name="Test User", role=UserRoles.user)


def fake_login_admin() -> dict:
    return TokenData(user_id="test_2", name="Test Admin", role=UserRoles.admin)
