# AAS Inference Engine

This project provides a base image with Gradio and Triton Client installed, as well as a Cookiecutter Template to create a Gradio application that calls Triton Inference Server.

## Getting Started

### Install Cookiecutter

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) is a CLI tool that generates a project from a project template. We will be using this tool for generating a template Inference Engine.

Install it as follows:

**Using pipx (recommended)**

[pipx](https://pypa.github.io/pipx/) is recommended as it will install Cookiecutter in an isolated environment, ensuring that there is no conflict with any of your dependencies.

```bash
pipx install cookiecutter
```

**Using pip**

```bash
pip install cookiecutter
```

**Using Poetry**
Within the repository, the `ai-model/inference-engine/pyproject.toml` contains Cookiecutter as a development dependency

```bash
poetry install
```

### Generate Project

Generate your project as follows
```bash
cookiecutter https://github.com/DinoHub/appstore-ai.git --directory inference-services/templates/gradio-app
```

Then, follow the prompts to generate a project template.

### Set up Development Environment

For development, it's suggested to set up a virtual environment for development. You can use any dependency manager you want, but the Dockerfile that is used to build the final image will read from a `requirements.txt` file by default.

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Example Apps

When generating a Cookiecutter template, we offer the option to generate a project based on an example task (e.g Image Classification).

#### What is Gradio?

> One of the best ways to share your machine learning model, API, or data science workflow with others is to create an interactive app that allows your users or colleagues to try out the demo in their browsers.
> Gradio allows you to build demos and share them, all in Python. - [Gradio Quickstart](https://gradio.app/quickstart/)

Gradio applications provide the AI App Store with a way to enable model developers to share their models, and let end users to try out the models.

### Creating a Gradio Application

The simplified structure of the generated project is as follows:

```
Your Gradio App/
├─ src/
│  ├─ app.py
│  ├─ config.py
│  ├─ predict.py
├─ Dockerfile
├─ Makefile
├─ requirements.txt

```

| File             | Purpose                                                                                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| src/app.py       | Main app. Imports the inputs, outputs and prediction function from `predict.py` and launches a Gradio app server                                            |
| src/predict.py   | You define the inputs, outputs and prediction function of the application in this file                                                                      |
| src/config.py    | Contains configuration that the app can use.                                                                                                                |
| Dockerfile       | Build instructions to build the image                                                                                                                       |
| requirements.txt | Details dependencies needed for the application to run. Note that by default, the base image already includes the `gradio` and `tritonclient` dependencies. |

#### Defining Inputs, Outputs and Examples

Under `predict.py`, you will find the following variables:

- `inputs`
- `outputs`
- `examples`

Relevant Documentation:

- [Gradio - The Interface Class](https://gradio.app/getting_started/#the-interface-class)
- [Gradio IO Components API Reference](https://gradio.app/docs/#components)
- [Gradio Guide on Providing Examples](https://gradio.app/key_features/#example-inputs)

#### Prediction Function

Under `predict.py` you will also find the `predict` function, which you will need to define. The inputs to the function correspond to the inputs specified in the `inputs` variable, while the returned variables must correspond to the `outputs` variable.

#### Setting up Configuration

You may need to store certain settings in your app, or load a setting from an environment variable. `config.py` offers a [Pydantic](https://pydantic-docs.helpmanual.io/usage/settings/) configuration object to fufill this need (`pydantic` is a dependency of `Gradio`)

```python
from typing import Optional
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    port: int = Field(default=8080, env="PORT") # load from $PORT if available, else 8080

    setting_1: str = "hello world"

config = Config()
```

See the example task configurations for ideas of what you can put in the configuration object.

### Submitting Your Inference Engine

#### Export Requirements

Assuming you are inside a virtual environment, run the following command to export your current dependencies:

```bash
pip freeze > requirements.txt
```

#### Build the Image

To build the Docker image, we provide a `Makefile` that has a command to build the image

Run the following command to build it

```bash
make build
```

#### Test the Image

To run the docker image and test it, run the following command

```bash
make run
```

#### Submit to Image Registry

#### Submitting to AI App Store

### Resources

- [Gradio Quickstart](https://gradio.app/getting_started/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/usage/settings/)

## FAQ

- Should I specify the port number for the Gradio app or expose it in the Dockerfile?
  - If you are submitting it on the AI App Store, it's not necessary as the KNative serving service automatially assigns a port number to it, setting it to the $PORT environment variable. Thus, it's better to get your app to listen to the $PORT environment variable.

## Licence

This project is under the [GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).

### TL;DR

You may copy, distribute and modify the software as long as you track changes/dates in source files. Any modifications to or software including (via compiler) GPL-licensed code must also be made available under the GPL along with build & install instructions.

## Contributors

### Core Contributors

- [Mathias Ho](https://github.com/OrionSolaris)
- [Tien Cheng](https://github.com/Tien-Cheng)

### Special Thanks

- Our project supervisor and mentor in DSTA Digital Hub, [Kah Siong](https://github.com/jax79sg)
