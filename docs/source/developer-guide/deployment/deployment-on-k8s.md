# Deployment of the AI Appstore on a K8S Cluster

## Configuring Helm Charts

### Configuring Hosts
The front-end and back-end are served behind an Nginx Ingress Controller. Therefore, you will need to do the following:
- Configure the Helm Chart values to define the hostnames of the back-end and front-end
- Get the static IP address of the Nginx Ingress
- Configure DNS to redirect the URL of the frontend/backend to the ingress

## Air-gapped Environment
In an environment without any access to the internet, some modifications need to be made.

### Transfering the Required Images
#### App Images
After building the images for the front-end and back-end, you will need to save them to a `.tar` file:
```bash
docker save aas-frontend:<tag> > aas-frontend.tar
docker save aas-backend:<tag> > aas-backend.tar
```

The saved images can then be transferred over to the air-gapped environment through an external device (e.g secured USB flash drive). Once transferred over, the images can be loaded as follows:
```bash
docker load -i aas-frontend.tar
docker load -i aas-backend.tar
```
#### Dependencies
The images for the dependencies also have to be saved and loaded.
### Pushing to the Private Registry
#### Logging In
If you are not already logged in to the cluster's private registry, do so right now
```bash
docker login <registry-url> -u <username> -p <password>
```
#### Tagging
Tag the images as follows:
```bash
docker tag aas-frontend:<tag> <registry-url>/<repository>/aas-frontend:tag
docker tag aas-backend:<tag> <registry-url>/<repository>/aas-backend:tag
```

#### Push
Then, push the images to the registry as follows:
```bash
docker push <registry-url>/<repository>/aas-frontend:tag
docker push <registry-url>/<repository>/aas-backend:tag
```
If you have not made the repository yet, you may get an error. In which case, you need to go to your private registry to make a new repository/project.

### Using Privately Hosted Images
The Helm charts can then be configured via the Values to pull in images from the private registry:

```yaml
image:
    repository: <registry-url>/<repository>/<image-name>
```

## Potential Issues

### Outdated Kubernetes Cluster
- If your K8S cluster is too old (< 1.20), the KNative backend for serving inference services will not work. As such, you have to use alternative backends such as the `emissary` backend. Note that other backends will not support auto-scaling from 0, meaning that the services will be always running and taking up resources on the cluster. 
- We do currently have a manual-scaling option in the user interface as an alternative.

### Self-Hosted ClearML
If attempting to connected to a self hosted ClearML server, you will need to provide the TLS certificates needed to connect to it, otherwise the ClearML integration will not work. 

This is supported by supplying the cert in the Helm chart values:

```bash
helm install ... --set-file certs.CA_CERT=<path to cert file>
```

### Storage Provisioning
It is possible that the K8S cluster may lack a dynamic storage provisioner. To check, run the following command: `kubectl get sc -A`. If no resources were found, it means you don't have a storage provisioner configured. This is problematic as MongoDB requires a persistent volume to persist it's data. To solve this, you need to manually provision storage as follows:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: aas-mongodb-pv
  namespace: ai-appstore
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 8Gi
  volumeMode: Filesystem
  storageClassName: aas-mongodb
  hostPath:
    path: "/bitnami/mongodb"
EOF
```