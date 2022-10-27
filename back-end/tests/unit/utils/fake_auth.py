def fake_login_user() -> dict:
    return dict(userId="test_1", name="Test User", adminPriv=False)


def fake_login_admin() -> dict:
    return dict(userId="test_1", name="Test User", adminPriv=True)
