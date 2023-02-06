from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.internal.utils import sanitize_for_url
from src.models.engine import (
    CreateInferenceEngineService,
    InferenceEngineService,
    InferenceServiceStatus,
    K8SPhase,
    UpdateInferenceEngineService,
)


@given(st.builds(InferenceServiceStatus))
def test_inference_service_status(status: InferenceServiceStatus):
    assert status.expected_replicas <= 1 and status.expected_replicas >= 0
    assert status.status in K8SPhase


@given(
    st.builds(
        CreateInferenceEngineService,
        # image_uri=st.from_regex(IMAGE_URI_REGEX),
    )
)
def test_create_inference_engine_service(
    service: CreateInferenceEngineService,
):
    assert service.num_gpus <= 2 and service.num_gpus >= 0
    assert service.model_id == sanitize_for_url(service.model_id)


@given(st.builds(InferenceEngineService))
def test_inference_engine_service(service: InferenceEngineService):
    assert service.num_gpus <= 2 and service.num_gpus >= 0
    assert service.model_id == sanitize_for_url(service.model_id)


@given(st.builds(UpdateInferenceEngineService))
def test_update_inference_engine_service(
    service: UpdateInferenceEngineService,
):
    assert service.num_gpus <= 2 and service.num_gpus >= 0
