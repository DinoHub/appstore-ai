import io
import json
import tempfile
from typing import List

import cv2
from fastapi import File, Form, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from render import (RAND_COLORS, get_text_size, render_box, render_filled_box,
                    render_text)
from schema import BoundingBox

CHUNK_SIZE = 1024


async def visualize(media: UploadFile = File(), outputs: str = Form()) -> StreamingResponse:
    # Attempt to decode output of model
    try:
        outputs: List[BoundingBox] = json.loads(outputs)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode JSON output of model",
        )
    try:
        with tempfile.NamedTemporaryFile() as f:
            while content := media.file.read(CHUNK_SIZE):
                f.write(content)
            # Assume that its an image (for now anyways)
            input_image = cv2.imread(f.name)
        if input_image is None:
            raise IOError
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when attempting to read file input",
        )

    # Render outputs
    detected = outputs["outputs"][0]
    for output in detected:
        print(output["class_name"])
        input_image = render_box(
            input_image,
            output["bbox"],
            color=tuple(RAND_COLORS[output["class_id"] % 64].tolist()),
        )
        size = get_text_size(
            input_image,
            f"{output['class_name']}: {output['confidence']:.2f}",
            normalised_scaling=0.6,
        )
        input_image = render_filled_box(
            input_image,
            (
                output["bbox"][0] - 3, # x1
                output["bbox"][1] - 3, # y1
                output["bbox"][0] + size[0], 
                output["bbox"][1] + size[1],
            ),
            color=(220, 220, 220),
        )
        input_image = render_text(
            input_image,
            f"{output['class_name']}: {output['confidence']:.2f}",
            (output["bbox"][0], output["bbox"][1]),
            color=(30, 30, 30),
            normalised_scaling=0.5,
        )
    input_image = cv2.imencode(
        ext=".jpg",
        img=input_image
    )[1] # hard-code to export image as jpeg

    return StreamingResponse(
        content=io.BytesIO(
            input_image.tobytes()
        ),
        media_type="image/jpeg"
    )
