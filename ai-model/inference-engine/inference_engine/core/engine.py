import json
import logging
from os import environ
from typing import Callable, Dict, List, Optional, Tuple

import uvicorn
import yaml
from fastapi import FastAPI, File, Form, Request, UploadFile, status
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException

from ..schemas.io import IOSchema
from ..schemas.metadata import Metadata
from ..utils.io import download_file, remove_unused_files


class InferenceEngine:
    def __init__(
        self,
        name: str = "Inference Engine",
        version: str = "v1",
        description: str = "Inference Engine for AI App Store",
        author: str = "Anonymous User",
        endpoint_metas: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> None:
        """Create an inference engine.


        :param name: _description_, defaults to "Inference Engine"
        :type name: str, optional
        :param version: _description_, defaults to "v1"
        :type version: str, optional
        :param description: _description_, defaults to "Inference Engine for AI App Store"
        :type description: str, optional
        """
        if endpoint_metas is None:
            endpoint_metas = {}  # TODO: Figure out what to do with metas
        self.logger = logging.Logger(name)
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.endpoint_metas: Optional[
            Dict[str, Dict[str, str]]
        ] = endpoint_metas
        self.engine = FastAPI(
            title=self.name, version=self.version, description=self.description
        )
        self.engine.add_api_route(
            path="/{endpoint}",
            endpoint=self._get_metadata,
            methods=["GET"],
            response_model=Metadata,
        )
        self.engine.add_api_route(
            path="/", endpoint=self._status, methods=["GET"]
        )
        self.endpoints: Dict[
            str, Tuple[Callable[[IOSchema], IOSchema], IOSchema, IOSchema]
        ] = {}

    def _get_metadata(self, endpoint: str) -> Metadata:
        try:
            _, input_schema, output_schema = self.endpoints[endpoint]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata for {endpoint} not found.",
            )
        return Metadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            input_schema=input_schema,
            output_schema=output_schema,
        )

    def _status(self):
        return {
            "message": "Hello World!",
            "metadata": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "author": self.author,
            },
        }

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
        self.engine.add_api_route(
            path=f"/{route}",
            endpoint=self._predict,
            methods=["POST"],
            # response_model=output_schema,
        )

    def _predict(
        self,
        background_tasks: BackgroundTasks,
        req: Request,
        media: Optional[List[UploadFile]] = File(None),
        text: Optional[str] = Form(None),
    ):
        # Process Inputs
        # Since we want similar processing of each registered,
        # endpoint, we use the same process function, but
        # dynamically get the user function.
        try:
            endpoint = req.url.path.strip("/")
            print(f"Endpoint: {endpoint}")
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
                self.logger.info("Converting text to JSON")
                text: Dict = json.loads(text)
                self.logger.warning(text)
                assert type(text) is dict
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to process text input as JSON: {e}",
                )
        inputs = input_schema(
            media=media, text=text
        )  # pydantic ignores undefined fields

        # Pass to user defined func
        outputs = executor(inputs)

        # Clean up input temp files (if any)
        # Return response
        if media is not None:
            # it is impt that the user function does not return
            # input file as response.
            background_tasks.add_task(remove_unused_files, media)
        # NOTE: if a custom schema does not confirm to using `media`,
        # as a reference to the filenames then this will not work.
        if "media" in outputs and outputs.media is not None:
            background_tasks.add_task(remove_unused_files, outputs.media)
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

    def serve(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        workers: Optional[int] = None,
    ):
        host = host or environ.get("HOSTNAME", default="0.0.0.0")
        port = port or int(environ.get("PORT", default=4001))
        workers = workers or int(environ.get("WORKERS", default=1))
        self.logger.info("Starting server")
        uvicorn.run(self.engine, host=host, port=port, workers=workers)
