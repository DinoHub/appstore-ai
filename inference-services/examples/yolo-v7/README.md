# yolo-v7

Inference service for AI App Store

## Model Description
YOLOv7 (You Only Look Once version 7) is a state-of-the-art object detection model developed for real-time object detection tasks. It is a deep learning model that has been trained on large datasets to identify and locate objects in an image or video.

## Model Usage
YOLOv7 can be used for various applications such as autonomous vehicles, security systems, and image and video analysis. It can be integrated into existing systems to add object detection capabilities. The model can be run on CPU or GPU and can be used for either image or video object detection.


## Model Explanation
YOLOv7 (You Only Look Once version 7) is a real-time object detection system that uses a single deep neural network to identify objects in an image. It is based on the YOLO (You Only Look Once) architecture, which was first introduced in 2015.

The process of YOLOv7 can be broken down into several stages:

1. Input Image Preprocessing: The input image is resized to a standard size, typically 416x416 pixels, and normalized to improve the accuracy of the deep neural network.

2. Object Detection: The image is passed through a deep neural network, which consists of several convolutional and fully connected layers. The network has been trained on a large dataset of annotated images, allowing it to detect objects within the image.

3. Prediction: The network generates predictions for bounding boxes and class probabilities for each object in the image. The bounding boxes indicate the location of the objects within the image, while the class probabilities indicate the confidence level of the prediction.

4. Non-Maximal Suppression: To eliminate overlapping or duplicate predictions, YOLOv7 applies Non-Maximal Suppression (NMS), which removes predictions that have a low confidence level or overlap with other predictions.

5. Output: The final output of YOLOv7 is a set of bounding boxes and class labels, along with the confidence level of each prediction.

YOLOv7 is designed to work in real-time, with a processing speed of up to 40-45 frames per second, making it suitable for use in a variety of applications, including self-driving cars, surveillance systems, and robotics.

## Model Limitations
- YOLOv7 is a deep learning model and requires a large amount of training data to perform well. It may not perform well on small or limited datasets.
- The model has been trained on a specific set of object categories, and may not be able to detect new or unseen objects.
- The model may struggle with occlusions, small objects, and similar objects with similar features.

## Model Performance
![](https://user-images.githubusercontent.com/26833433/136901921-abcfcd9d-f978-4942-9b97-0e3f202907df.png)

YOLOv7 has achieved state-of-the-art performance on several benchmark datasets for object detection tasks. It is one of the fastest object detection models, making it suitable for real-time applications. However, the exact performance of the model may vary depending on the specific use case and dataset.

## Build
To build the docker container, run
```sh
make build
```

### Push to Registry
To push the image to a registry, first build the image, then run
```sh
docker tag yolo-v7:1.0.0 <REGISTRY>/<REPO>/yolo-v7:1.0.0
```

If not logged in to the registry, run
```sh
docker login -u <USERNAME> -p <PASSWORD> <REGISTRY>
```

Then, push the tagged image to a registry
```sh
docker push <REGISTRY>/<REPO>/yolo-v7:1.0.0
```

## Run Locally
To run the Gradio application locally, run the following
```sh
make dev
```

## Deploy
First, make sure your image is pushed to the registry.

### Deployment on AI App Store
Check out the AI App Store documentation for full details, but in general:
1. Create/edit a model card
2. Pass the docker image URI (e.g `<REGISTRY>/<REPO>/yolo-v7:1.0.0`) when creating/editing the inference service

### Other Deployment Options
There are other potential deployment options, including:
- Google Cloud Run
- AWS Fargate
- Red Hat Openshift Serverless