from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.models.iam import UserInsert

password_strategy = st.from_regex(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(
    st.builds(
        UserInsert,
        password=st.shared(password_strategy, key="password"),
        password_confirm=st.shared(password_strategy, key="password"),
    )
)
def test_user_insert(user: UserInsert):
    assert user.password == user.password_confirm
