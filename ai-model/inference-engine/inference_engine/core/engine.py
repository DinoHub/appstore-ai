import json
from typing import Callable, Dict, List, Optional, Tuple

import yaml
from fastapi import FastAPI, File, Form, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from ..schemas.io import IOSchema
from ..schemas.metadata import Metadata
from ..utils.io import download_file


class InferenceEngine:
    def __init__(
        self,
        name: str = "Inference Engine",
        version: str = "v1",
        description: str = "Inference Engine for AI App Store",
        author: str = "Anonymous User",
    ) -> None:
        """Create an inference engine.


        :param name: _description_, defaults to "Inference Engine"
        :type name: str, optional
        :param version: _description_, defaults to "v1"
        :type version: str, optional
        :param description: _description_, defaults to "Inference Engine for AI App Store"
        :type description: str, optional
        """
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.engine = FastAPI(
            title=self.name, version=self.version, description=self.description
        )
        self.engine.add_api_route(
            path="/engine/{endpoint}",
            endpoint=self._predict,
            methods=["POST"],
        )
        self.engine.add_api_route(
            path="/",
            endpoint=self._get_metadata,
            methods=["GET"],
            response_model=Metadata,
        )
        self.endpoints: Dict[
            str, Tuple[Callable[[IOSchema], IOSchema], IOSchema, IOSchema]
        ] = {}

    def _get_metadata(self, endpoint: str) -> Metadata:
        _, input_schema, output_schema = self.endpoints[endpoint]
        return Metadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            input_schema=input_schema,
            output_schema=output_schema,
        )

    @classmethod
    def from_dict(cls, config: Dict) -> "InferenceEngine":
        executor = cls(**config)
        return executor

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "InferenceEngine":
        """From user specification, create inference engine

        :param yaml_path: _description_
        :type yaml_path: str
        :return: _description_
        :rtype: InferenceEngine
        """
        with open(yaml_path, "r") as f:
            config: Dict = yaml.safe_load(f)
        return cls.from_dict(config)

    def _register(
        self,
        route: str,
        func: Callable,
        input_schema: IOSchema,
        output_schema: IOSchema,
    ):
        # Create function
        # We register the user function so our endpoint can access them
        self.endpoints[route] = (func, input_schema, output_schema)

    def _predict(
        self,
        endpoint: str,
        media: Optional[List[UploadFile]] = File(None),
        text: Optional[str] = Form(None),
    ):
        # Process Inputs
        # We register a single endpoint, but this single endpoint,
        # can handle different possible subendpoints
        # which the user registers, so long as the endpoints follow the
        # set schema
        try:
            executor, input_schema, _ = self.endpoints[endpoint]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Endpoint {endpoint} does not exist.",
            )
        if media is not None:
            try:
                # Add files to input
                media = [download_file(file) for file in media]
                # Return just the file directory (since infer function runs on same pod)
                # so no need to store all in memory
            except IOError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unable to download media file due to error: {e}",
                )
        if text is not None:
            # Add form data to input
            # Convert first to JSON
            try:
                text = json.loads(text)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to process text input as JSON: {e}",
                )
        inputs = input_schema(media, text)  # pydantic ignores undefined fields

        # Pass to user defined func
        outputs = executor(inputs)

        # Return response
        return outputs.response()

    def entrypoint(
        self, func: Callable, input_schema: IOSchema, output_schema: IOSchema
    ):
        return self._register(
            "predict",
            func=func,
            input_schema=input_schema,
            output_schema=output_schema,
        )
