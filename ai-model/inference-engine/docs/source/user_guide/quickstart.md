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

def predict(data: TextIO) -> SingleMediaFileIO:
    text = data.text

    image = fake_client.predict(text)

    path = "tmp.png"
    image.save(path)

    return SingleMediaFileIO(
        media=[path],
        media_type="image/png"
    )

```

Edit the `Dockerfile` and `requirements.txt` file if you need to install any packages.

## Prerequisites


## Setting up Metadata

## Setting up Requirements

## Deciding on Input and Output Schemas


## Creating your Inference Function

## Registering Your Function

## Containerizing the Application


## Submitting the Inference Engine

```{warning}
This part is currently still WIP
```

---
{ref}`genindex` | {ref}`modindex`
