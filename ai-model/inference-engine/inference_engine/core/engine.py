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


        :param name: Name of Inference Engine, defaults to "Inference Engine"
        :type name: str, optional
        :param version: Version, defaults to "v1"
        :type version: str, optional
        :param description: Description of Inference Engine, defaults to "Inference Engine for AI App Store"
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
            path="/", endpoint=self._status, methods=["GET"]
        )
        self.endpoints: Dict[
            str, Tuple[Callable[[IOSchema], IOSchema], IOSchema, IOSchema]
        ] = {}

    def _status(self) -> Dict:
        """Status endpoint for inference engine.

        :return: Metadata of inference engine
        :rtype: Dict
        """
        return {
            "message": "Hello World!",
            "metadata": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "author": self.author,
                "endpoints": self.endpoint_metas,
            },
        }

    @classmethod
    def from_dict(cls, config: Dict) -> "InferenceEngine":
        """Generate an inference engine from a dictionary.

        :param config: Configuration dictionary
        :type config: Dict
        :return: Inference Engine
        :rtype: InferenceEngine
        """
        if "metadata" not in config:
            config["metadata"] = {
                "name": "Inference Engine",
                "version": "v1",
                "author": "Unknown",
                "description": "",
            }
        if "endpoints" not in config:
            config["endpoints"] = None
        try:
            executor = cls(
                name=config["metadata"]["name"],
                version=config["metadata"]["version"],
                author=config["metadata"]["author"],
                description=config["metadata"]["description"],
                endpoint_metas=config["endpoints"],
            )
        except KeyError as e:
            raise ValueError(f"Field not supplied: {e}")
        return executor

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "InferenceEngine":
        """From user specification, create inference engine

        :param yaml_path: Path to yml config
        :type yaml_path: str
        :return: Inference Engine
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
        media_type: Optional[str] = None,
    ) -> None:
        """Register a function to be called when a request is made to the
        route of the inference engine.

        :param route: Route to register function to
        :type route: str
        :param func: Function to register
        :type func: Callable
        :param input_schema: IOSchema used to process request input
        :type input_schema: IOSchema
        :param output_schema: IOSchema used to process and send back response
        :type output_schema: IOSchema
        :param media_type: If any media (e.g images) are returned, their MIME type, defaults to None
        :type media_type: Optional[str], optional
        """
        # Create function
        # We register the user function so our endpoint can access them
        self.endpoints[route] = (func, input_schema, output_schema)

        # Check if already defined in schema
        if route in self.endpoint_metas:
            self.logger.warning("Found existing config with same route")
            existing_data = self.endpoint_metas[route]
            if (
                media_type != existing_data["media_type"]
                or input_schema.__name__ != existing_data["input_schema"]
                or output_schema.__name__ != existing_data["output_schema"]
            ):
                # If so, check if any changes and override
                self.logger.warning(
                    "Existing config is different, overriding it with new function."
                )
                self.endpoint_metas[route] = {
                    "type": "POST",
                    "input_schema": input_schema.__name__,
                    "output_schema": output_schema.__name__,
                    "media_type": media_type,
                }
        self.engine.add_api_route(
            path=f"/{route}",
            endpoint=self._predict,
            methods=["POST"],
        )

    def _predict(
        self,
        background_tasks: BackgroundTasks,
        req: Request,
        media: Optional[List[UploadFile]] = File(None),
        text: Optional[str] = Form(None),
    ):
        """Wrapper function around user function to process request and
        response.

        :param background_tasks: Perform cleanup task to remove tmp files
        :type background_tasks: BackgroundTasks
        :param req: User request to get the endpoint name
        :type req: Request
        :param media: Any files sent in request, defaults to File(None)
        :type media: Optional[List[UploadFile]], optional
        :param text: Stringified JSON sent as input, defaults to Form(None)
        :type text: Optional[str], optional
        :raises HTTPException: 422 if failed to process input
        :return: Response, as decided by output IOSchema
        :rtype: Response
        """
        # Process Inputs
        # Since we want similar processing of each registered,
        # endpoint, we use the same process function, but
        # dynamically get the user function.
        endpoint = req.url.path.strip("/")
        executor, input_schema, _ = self.endpoints[endpoint]
        media_type = self.endpoint_metas[endpoint]["media_type"]
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
        return outputs.response(media_type=media_type)

    def entrypoint(
        self,
        func: Callable,
        input_schema: IOSchema,
        output_schema: IOSchema,
        media_type: Optional[str] = None,
    ) -> None:
        """Default entrypoint for inference engine.
        Is just a wrapper around _register with
        pre-defined route (`predict`)

        :param func: User function to register
        :type func: Callable
        :param input_schema: IOSchema used to process request input
        :type input_schema: IOSchema
        :param output_schema: IOSchema used to process and send back response
        :type output_schema: IOSchema
        :param media_type: If any media (e.g images) are returned, their MIME type, defaults to None
        :type media_type: Optional[str], optional
        """
        return self._register(
            "predict",
            func=func,
            input_schema=input_schema,
            output_schema=output_schema,
            media_type=media_type,
        )

    def serve(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        workers: Optional[int] = None,
    ) -> None:
        """Serve the inference engine.

        :param host: Hostname, if none provided will use either environment variable or 0.0.0.0, defaults to None
        :type host: Optional[str], optional
        :param port: Port, if none provided will use either environent variable or 4001, defaults to None
        :type port: Optional[int], optional
        :param workers: Number of workers to serve concurrent requests, if none provided uses environment variable or 1, defaults to None
        :type workers: Optional[int], optional
        """
        host = host or environ.get("HOSTNAME", default="0.0.0.0")
        port = port or int(environ.get("PORT", default=4001))
        workers = workers or int(environ.get("WORKERS", default=1))
        self.logger.info("Starting server")
        uvicorn.run(self.engine, host=host, port=port, workers=workers)
