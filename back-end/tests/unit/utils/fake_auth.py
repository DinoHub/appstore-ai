def fake_login_user() -> dict:
    return dict(userid="test_1", name="Test User", admin_priv=False)


def fake_login_admin() -> dict:
    return dict(userid="test_1", name="Test User", admin_priv=True)
