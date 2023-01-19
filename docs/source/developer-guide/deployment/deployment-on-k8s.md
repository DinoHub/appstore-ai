# Deployment of the AI Appstore on a K8S Cluster

## Prerequisite Tools

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/)
- [Docker](https://www.docker.com/)

## Building the Images

To build the images, run the following command in the root of the project directory

```bash
sh build-images.sh <version number>
```

where `<version number>` is the application version (e.g 1.1.0)

## Configuring Helm Charts

Before deploying the application as a Helm chart, you will need to configure the values/settings of the Helm chart, to suit your deployment needs.

### Configuring Dependencies

#### MongoDB (`k8s/charts/dependencies/mongodb`)

The following values need to be replaced:

- The service account credentials will be used by the AI App Store backend to connect to the MongoDB. We make use of a user that only has access to the AI App Store database for better security. Do not give the back-end the root account credentials.

| Field             | Type   | Description                                                      | Example          |
| ----------------- | ------ | ---------------------------------------------------------------- | ---------------- |
| auth.rootUser     | string | Username of the MongoDB system admin                             | root             |
| auth.rootPassword | string | Password of the MongoDB system admin                             | p@ssw0rd         |
| auth.usernames[0] | string | Fill this with the username of the service account               | aasDbServiceAcct |
| auth.passwords[0] | string | Fill this with the password of the service account               | serviceP@ssw0rd  |
| auth.databases[0] | string | Fill this with the name that will be used by the service account | appStoreProdDb   |

#### Emissary

In theory, no values have to be changed here, but in the case of deployment to an airgapped environment, you will need to change the repository to the private cluster registry.

##### Emissary CRDs (`k8s/charts/dependencies/emissary-crds`)

Emissary CRDs need to be installed first for Emissary to install properly

| Field                   | Type   | Description            | Example                            |
| ----------------------- | ------ | ---------------------- | ---------------------------------- |
| apiext_image.repository | string | Repo for main Emissary | docker.io/emissaryingress/emissary |
| apiext_image.tag        | string | Image tag              | 3.4.0                              |

##### Emissary (`k8s/charts/dependencies/emissary-ingress`)

| Field                  | Type   | Description            | Example                               |
| ---------------------- | ------ | ---------------------- | ------------------------------------- |
| image.repository       | string | Repo for main Emissary | docker.io/emissaryingress/emissary    |
| image.tag              | string | Image tag              | 3.4.0                                 |
| agent.image.repository | string | Repo for main Emissary | docker.io/ambassador/ambassador-agent |
| agent.image.tag        | string | Image tag              | 1.0.3                                 |

#### KNative

#### MinIO (Optional)

If you already have S3 storage set up (e.g AWS ECS, GCP GCS), you do not need to deploy the MinIO helm chart. MinIO is simply an open sourced S3 provider.

| Field                 | Type   | Description                                 | Example              |
| --------------------- | ------ | ------------------------------------------- | -------------------- |
| rootUser              | string | Username of root admin                      | root                 |
| rootPassword          | string | Password of root admin                      | RootTempPassword1234 |
| users[0].accessKey    | string | Access key of normal user.                  | ai-appstore          |
| users[0].secretKey    | string | Secret key of normal user.                  | TempPassword1234     |
| users[0].policy       | string | Access level of user. Recommend `readwrite` | readwrite            |
| svcaccts[0].accessKey | string | Access key of service account               | aas-minio-uploader   |
| svcaccts[0].secretKey | string | Secret key of service account               | TempPassword         |
| svcaccts[0].user      | string | User to link service account permissions to | ai-appstore          |
| ingress.hosts[0]      | string | Hostname to access Minio by                 | storage.appstore.ai  |

### Configuring Backend

| Field                     | Type   | Description                                                                                 | Example            |
| ------------------------- | ------ | ------------------------------------------------------------------------------------------- | ------------------ |
| env.PROD_FRONTEND_HOST    | string | Frontend origin for CORS                                                                    | http://appstore.ai |
| env.PROD_SECURE_COOKIES   | string | If connection with frontend is secure HTTPS connection, this should be `true`, else `false` | false              |
| env.PROD_SECRET_KEY       | string | Used to hash the password                                                                   | hello              |
| env.PROD_ADMIN_SECRET_KEY | string | Used to hash the admin account passwords                                                    | hello2             |
| env.PROD_ALGORITHM        | string | Hashing algorithm used                                                                      | HS256              |

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
