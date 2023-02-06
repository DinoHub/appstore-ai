from hypothesis import given
from hypothesis import strategies as st

from src.internal.utils import sanitize_for_url
from src.models.common import PyObjectId
from src.models.model import (
    ModelCardModelDB,
    ModelCardModelIn,
    UpdateModelCardModel,
)


@given(st.builds(ModelCardModelIn))
def test_model_card_model_in(card: ModelCardModelIn):
    assert len(card.title) <= 50
    for tag in card.tags:
        assert isinstance(tag, str)

    for framework in card.frameworks:
        assert isinstance(framework, str)


@given(st.builds(ModelCardModelDB))
def test_model_card_model_db(card: ModelCardModelDB):
    assert len(card.title) <= 50
    for tag in card.tags:
        assert isinstance(tag, str)

    for framework in card.frameworks:
        assert isinstance(framework, str)

    assert isinstance(card.id, PyObjectId)

    # check model_id doesn't have any unsafe characters
    assert card.model_id == sanitize_for_url(card.model_id)

    # TODO: currently not testing for created and last_modified
    # as they are strings


@given(
    st.builds(
        UpdateModelCardModel,
        created=st.datetimes(),
        last_modified=st.datetimes(),
    )
)
def test_update_model_card_model(card: UpdateModelCardModel):
    if card.title:
        assert len(card.title) <= 50

    if card.tags:
        for tag in card.tags:
            assert isinstance(tag, str)

    if card.frameworks:
        for framework in card.frameworks:
            assert isinstance(framework, str)
