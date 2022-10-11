# Quickstart
This section will guide you through creating your own inference engine for use with the AI App Store

## TL;DR
Install this package as follows
```bash
pip install -i https://test.pypi.org/simple/ inference-engine
```

Then, use the generator to create a template Inference Engine
```bash
python -m inference-engine new engine
```

Edit the `predict` function in `process.py` to process the input and then return the output. For instance,

```python
def predict(data: TextIO) -> MediaFileIO:
    text = data.text

    image = fake_client.predict(text)

    path = "tmp.png"
    image.save(path)

    return MediaFileIO(
        media=dict(output=[path]),
    )

```

Edit the `Dockerfile` and `requirements.txt` file if you need to install any packages.

## Prerequisites
To install the library, run

```bash
pip install -i https://test.pypi.org/simple/ inference-engine
```

There are also addon options which include other useful libraries as additional dependencies.

### Triton Inference Server
To install the Triton Client (currently installs only the GRPC client), install using the following command

```bash
pip install -i https://test.pypi.org/simple/ inference-engine[triton]
```

## Creating an Inference Engine
### CLI Generator
The library includes a CLI program to generate a template inference engine for you. 

You can run it with the following command:
```bash
python -m inference_engine new engine
```

You can then follow the prompts in the setup tool to generate a new inference engine. 

### Manual
You can also just create your own Inference Engine manually without using the CLI tool.

The most basic structure of an inference engine just consists of 
- a `main.py` script (as of this version, the file must be called `main.py`, otherwise the Dockerfile must override the `CMD` to run the script)
- a `Dockerfile` to build the inference engine image

In addition, you may also want to include
- a `config.yaml` file to store metadata on the Inference Engine. Otherwise, the inference engine will have to be initialized via a config dictionary
- a `requirements.txt` file to list out any Python dependencies.

### Setting up Metadata
It is necessary to define metadata for the inference engine. 

The schema for this configuration can be found here: {doc}`/user_guide/ie_yaml_schema`

This information can be specified as
- a YAML file
- a Python Dictionary

An example config yaml is shown below:
```yaml
schema_version: 2
metadata:
  name: Model V1
  version: v1
  description: Example user inference engine
  author: User
endpoints:
  predict:
    type: POST
    input_schema: TextIO
    output_schema: MediaFileIO
```
### Deciding on Input and Output Schemas
In the Inference Engine, {doc}`IOSchema</api/inference_engine.schemas.io.IOSchema>` offers an interface for your inference engine to receive input, and return your output to be sent back to the user.

A schema may expose two main attributes by which data can be accessed and stored:

`.text`
: A dictionary where keys are fieldnames, and values contain corresponding field values. Field values do not necessarily need to be text, JSONable objects (e.g Dictionaries) can be stored here as well,

`.media`
: A dictionary where keys are fieldnames, and values are lists that contain filepaths to the files corresponding to that field. When receiving file data, the inference engine automatically downloads the files and will autopopulate `.media` with the filepaths.

#### Types of IOSchemas
Several options can be selected for use as IOSchema for input and output types. They are:
##### {doc}`GenericIO</api/inference_engine.schemas.io.GenericIO>`
Contains both text and media to allow for mixed input and output. If used to send an output, all media files returned in the response will automatically be converted to Base64. The media type of any media files uploaded will be stored in the `media_types` mapping in the returned response.

```python
from inference_engine import GenericIO

data = MediaFileIO(
    text={
        "text_field" : "hello world",
        "json_field" : {
            "nested_field" : "nested_value"
        }
    },
    media={
        "images" : ["image1.png", "image2.png"],
        "targets" : ["target1.png", "target2.png"]
    }
)
```
##### {doc}`JSONIO</api/inference_engine.schemas.io.JSONIO>`
Contains only the `.text` attribute, where keys are fieldnames and values can be anything (e.g strings, dictionary) so long as the overall `.text` dictionary can be encoded as a JSON string

```python
from inference_engine import JSONIO

data = MediaFileIO(
    text={
        "text_field" : "hello world",
        "json_field" : {
            "nested_field" : "nested_value"
        }
    }
)
```

##### {doc}`TextIO</api/inference_engine.schemas.io.TextIO>`
Unlike {doc}`JSONIO</api/inference_engine.schemas.io.JSONIO>`, the `.text` attribute is a string that can store only a single value. This exists mostly as a form of syntax sugar to access the text if there is only a single form input.

```python
from inference_engine import TextIO

data = TextIO(text={"text" : "hello world"})
print(data.text) # hello world
```

##### {doc}`MediaFileIO</api/inference_engine.schemas.io.MediaFileIO>`
Contains only `.media` attribute, which will be a dictionary where the keys are the form field name and values will be lists of file paths corresponding to that field. If used in the output, and only a single file is returned, we will directly stream the file as a response. Otherwise, the media files will be encoded in Base64.
The media type of any media files uploaded will be stored in the `media_types` mapping in the returned response (or in the `Content-Type` of the header for a single file response)

```python
from inference_engine import MediaFileIO

data = MediaFileIO(
    media={
        "files" : ["image.png"]
    }
)
```

### Creating your Inference Function

```python
from inference_engine import InferenceEngine

engine = InferenceEngine.from_yaml("config.yaml")

if __name__ == "__main__":
    engine.serve()
```

### Registering Your Function

```python
from inference_engine import MediaFileIO, TextIO
def predict(data: TextIO) -> MediaFileIO:
    text = data.text

    # ... processing code

    return MediaFileIO(
        media={
            "output" : "output.png"
        }
    )

```

```python
from inference_engine import InferenceEngine, MediaFileIO, TextIO
from process import predict

engine = InferenceEngine.from_yaml("config.yaml")
engine.entrypoint(predict, TextIO, MediaFileIO)

if __name__ == "__main__":
    engine.serve()
```

### Containerizing the Application
To containerize the application, you first need a `Dockerfile`, which defines the build instructions to build an image from your application. It is highly recommended to build the image from the base `inference-engine` image, which has the library pre-installed.

An example `Dockerfile` is shown below
```dockerfile
FROM tiencheng/inference-engine:latest

COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt

ARG PORT=4001
ENV PORT=${PORT}

EXPOSE ${PORT}

COPY . .
```

Then, the image can be built as follows:
```bash
docker build . -t <tag name>
```

Once the image is built, it can be published to an image repository
```bash
docker tag <local tag> <remote tag>
docker push <remote tag>
```


### Submitting the Inference Engine
The AI App Store is able to take your image, and deploy it in it's back-end as a KNative Service from which the App Store is able to call it.

```{warning}
This part is currently still WIP
```

---
{ref}`genindex` | {ref}`modindex`
