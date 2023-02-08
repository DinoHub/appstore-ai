# Developing on Kubernetes

To develop on Kubernetes, you will need to have a Kubernetes cluster running. We recommend using [K3d](https://k3d.io/) to run a local Kubernetes cluster. You can also use [Kind](https://kind.sigs.k8s.io/) or [Minikube](https://minikube.sigs.k8s.io/). You will also need to have [Skaffold](https://skaffold.dev/) installed. Skaffold is a tool that facilitates continuous development for Kubernetes applications. It is used to build and deploy the project to the Kubernetes cluster. We recommend using the [recommended installation method](https://skaffold.dev/docs/install/) for your operating system.

## Creating a Kubernetes Cluster

### K3d

To create a Kubernetes cluster using K3d, run the following command:

```bash
k3d cluster create k3d-cluster
```

### Kind

To create a Kubernetes cluster using Kind, run the following command:

```bash
sh k8s/environments/development/cluster/generate-ip-address-pool-kind.sh &&	kind create cluster --config k8s/environments/development/cluster/kind.yaml
```

## Configuring Development Environment

Inside k8s/environments/development, there are files that are used to configure the development environment. Usually, you will not need to change these files. However, if you need to change the configuration, you can do so by editing the files in this folder.

## Deploying to Kubernetes

We use Skaffold, a tool that facilitates continuous development for Kubernetes applications, to deploy the project to the Kubernetes cluster. To deploy the project to the Kubernetes cluster, run the following command:

```bash
skaffold run
```

To deploy the project in dev mode (with hot reload)ing), run the following command:

```bash
skaffold dev
```

## Note

### Kind

- To ensure the MetalLB load balancer has the correct IP address, run the following command:

```bash
sh k8s/environments/development/cluster/generate-ip-address-pool-kind.sh
```

Then, it will generate a MetalLB config manifest that needs to be applied.

- To load images into the Kind cluster, run the following command:

```bash
kind load docker-image <image name>
```
