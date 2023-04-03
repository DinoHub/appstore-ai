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

## Creating Namespaces

Run the following to create the namespaces that will be used by the application:

```bash
kubectl apply -f k8s/namespaces.yaml
```

This will create the following namespaces:

- `ai-appstore`
- `inference-engine`
- `kourier-system`
- `knative-serving`

## Configuring Helm Charts

Before deploying the application as a Helm chart, you will need to configure the values/settings of the Helm chart, to suit your deployment needs.

Instead of directly editing the `values.yaml` in the Helm chart, we recommend configuring a separate values file found in the `k8s/environments/production` directory.

### Configuring Dependencies

#### MongoDB (`k8s/charts/dependencies/mongodb`)

The following values need to be replaced in `:

- The service account credentials will be used by the AI App Store backend to connect to the MongoDB. We make use of a user that only has access to the AI App Store database for better security. Do not give the back-end the root account credentials.

Configuration File: `k8s/environments/production/mongodb-values.yaml`
| Field | Type | Description | Example |
| ----------------- | ------ | ---------------------------------------------------------------- | ---------------- |
| auth.rootUser | string | Username of the MongoDB system admin | root |
| auth.rootPassword | string | Password of the MongoDB system admin | p@ssw0rd |
| auth.usernames[0] | string | Fill this with the username of the service account | aasDbServiceAcct |
| auth.passwords[0] | string | Fill this with the password of the service account | serviceP@ssw0rd |
| auth.databases[0] | string | Fill this with the name that will be used by the service account | appStoreProdDb |
| persistence.storageClass | string | PVC Storage Class for MongoDB data volume. By default this should be left alone unless you need to [manually provision storage](#storage-provisioning), in which case it should be set to the name of the storage class given when defining the persistent volume | |

#### Emissary

In theory, no values have to be changed here, but in the case of deployment to an airgapped environment, you will need to change the repository to the private cluster registry.

##### Emissary CRDs (`k8s/charts/dependencies/emissary-crds`)

Emissary CRDs need to be installed first for Emissary to install properly

Configuration File: `k8s/environments/production/emissary-crd-values.yaml`
| Field | Type | Description | Example |
| ----------------------- | ------ | ---------------------- | ---------------------------------- |
| apiext_image.repository | string | Repo for main Emissary | docker.io/emissaryingress/emissary |
| apiext_image.tag | string | Image tag | 3.4.0 |

##### Emissary (`k8s/charts/dependencies/emissary-ingress`)

Configuration File: `k8s/environments/production/emissary-values.yaml`
| Field | Type | Description | Example |
| ---------------------- | ------ | ---------------------- | ------------------------------------- |
| image.repository | string | Repo for main Emissary | docker.io/emissaryingress/emissary |
| image.tag | string | Image tag | 3.4.0 |
| agent.image.repository | string | Repo for main Emissary | docker.io/ambassador/ambassador-agent |
| agent.image.tag | string | Image tag | 1.0.3 |

#### KNative

Note that KNative requires a Kubernetes cluster with minimum version 1.20.0. As such, make sure to check the cluster version before attempting to install. Otherwise, the installation will fail even if you configured the Helm chart properly.

Configuration File: `k8s/environments/production/aas-knative-backend-values.yaml`

| Field          | Type                | Description                                                                                                                                                                                                                                                                                                                                  | Example             |
| -------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| domain.enabled | boolean             | If you have configured DNS for Knative, you should enable this                                                                                                                                                                                                                                                                               | true                |
| domain.name    | string              | Domain                                                                                                                                                                                                                                                                                                                                       | knative.example.com |
| baseImages     | map[string, string] | KNative relies on a bunch of images. If in an airgapped environment, you need to pass the full image URI to all KNative to pull these images from a private registry. If you are able to access the internet, just remove this whole key from the config values file to default to the normal repositories that KNative stores its images in |

#### MinIO (Optional)

If you already have S3 storage set up (e.g AWS ECS, GCP GCS), you do not need to deploy the MinIO helm chart. MinIO is simply an open sourced S3 provider.

Configuration File: `k8s/environments/production/minio-values.yaml`
| Field | Type | Description | Example |
| --------------------- | ------ | ------------------------------------------- | -------------------- |
| rootUser | string | Username of root admin | root |
| rootPassword | string | Password of root admin | RootTempPassword1234 |
| users[0].accessKey | string | Access key of normal user. | ai-appstore |
| users[0].secretKey | string | Secret key of normal user. | TempPassword1234 |
| users[0].policy | string | Access level of user. Recommend `readwrite` | readwrite |
| svcaccts[0].accessKey | string | Access key of service account | aas-minio-uploader |
| svcaccts[0].secretKey | string | Secret key of service account | TempPassword |
| svcaccts[0].user | string | User to link service account permissions to | ai-appstore |
| ingress.hosts[0] | string | Hostname to access Minio by | storage.appstore.ai |

### Configuring Backend

Now, it's time to configure the backend of the application.

Note that if your ClearML is self-hosted, you may need to follow the instructions [here](#https-certificates) to pass the CA certs to allow the backend to access ClearML without errors.

Configuration File: `k8s/environments/production/aas-backend-values.yaml`

| Field                             | Type                    | Description                                                                                                                                                                                                       | Example                              |
| --------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| image.repository                  | string                  | Image to pull for backend                                                                                                                                                                                         | registryname/ai-appstore/aas-backend |
| image.tag                         | string                  | Image tag to pull                                                                                                                                                                                                 | 1.10                                 |
| env.PROD_FRONTEND_HOST            | string                  | Frontend origins for CORS as a JSON array                                                                                                                                                                         | `'["http://web.appstore.ai"]'`       |
| env.PROD_SECURE_COOKIES           | string                  | If connection with frontend is secure HTTPS connection, this should be `true`, else `false`                                                                                                                       | false                                |
| env.PROD_SECRET_KEY               | string                  | Used to encrypt JWTs                                                                                                                                                                                              | 3ea9b3165966ef2517bd8f90642270774b54ded224941211dc68d966681bb998                                |                        |
| env.PROD_ALGORITHM                | string                  | Hashing algorithm used                                                                                                                                                                                            | HS256                                |
| env.PROD_MONGO_DSN                | string                  | MongoDB Domain Source Name, which should point to the location of your MongoDB (e.g a domain name, IP address)                                                                                                    | mongodb://aas-mongodb                |
| env.PROD_DB_NAME                  | string                  | Name of the MongoDB database to connect to. If you have configured the MongoDB Helm chart, this should correspond to the name of the database that the service account has been assigned to (`auth.databases[0]`) | appStoreProdDb                       |
| env.PROD_MONGO_USERNAME           | string                  | Username of MongoDB account. This should correspond to `auth.usernames[0]`                                                                                                                                        | aasDbServiceAcct                     |
| env.PROD_MONGO_PASSWORD           | string                  | Password of MongoDB account. This should correspond to `auth.passwords[0]`                                                                                                                                        | serviceP@ssw0rd                      |
| env.PROD_IE_NAMESPACE             | string                  | Namespace where any user inference services will be installed to                                                                                                                                                  | inference-engine                     |
| env.PROD_IE_SERVICE_TYPE          | `'emissary'\|'knative'` | What should be used to serve a user inference service?                                                                                                                                                            | emissary                             |
| env.PROD_IE_DEFAULT_PROTOCOL      | `'http'\|'https'`       | If you have configured KNative to obtain TLS cert, you should set this to `https`                                                                                                                                 |
| env.PROD_MINIO_DSN                | string                  | S3 Storage Domain Source Name, which should point to the location of your S3 (note that it does not need to be Minio, it could be something like AWS ECS)                                                         | minio:9000                           |
| env.PROD_MINIO_BUCKET_NAME        | string                  | Name of S3 bucket                                                                                                                                                                                                 | model-zoo                            |
| env.PROD_MINIO_TLS                | `'True'\|'False'`       | If connection to S3 needs to be secured                                                                                                                                                                           | False                                |
| env.PROD_MINIO_API_HOST           | string                  | Hostname of S3                                                                                                                                                                                                    | storage.appstore.ai                  |
| env.PROD_MINIO_API_ACCESS_KEY     | string                  | S3 Credentials Access Key                                                                                                                                                                                         | my_access_key                        |
| env.PROD_MINIO_API_SECRET_KEY     | string                  | S3 Credentials Secret Key                                                                                                                                                                                         | my_secret_key                        |
| env.PROD_FIRST_SUPERUSER_ID       | string                  | When creating the AI App Store, the app will create a root user. This is the username of that root user                                                                                                           | root                                 |
| env.PROD_FIRST_SUPERUSER_PASSWORD | string                  | Password of the first root user                                                                                                                                                                                   | P@ssw0rd                             |
| env.CLEARML_WEB_HOST              | string                  | Hostname of ClearML Web                                                                                                                                                                                           | app.clear.ml                         |
| env.CLEARML_API_HOST              | string                  | Hostname of ClearML API Server                                                                                                                                                                                    | api.clear.ml                         |
| env.CLEARML_FILES_HOST            | string                  | Hostname of ClearML File Server                                                                                                                                                                                   | files.clear.ml                       |
| env.CLEARML_API_ACCESS_KEY        | string                  | ClearML Credential Access Key                                                                                                                                                                                     | my_access_key                        |
| env.CLEARML_API_SECRET            | string                  | ClearML Credential Secret Key                                                                                                                                                                                     | my_secret_key                        |
| inferenceServiceBackend.emissary  | boolean                 | Enable to support use of Emissary. This creates the necessary permissions needed for back-end to interact with Emissary                                                                                           | true                                 |
| inferenceServiceBackend.knative   | boolean                 | Enable to support use of KNative. This enables the necessary permissions needed for back-end to interact with KNative                                                                                             | true                                 |
| ingress.hosts[0].host             | string                  | Hostname of backend                                                                                                                                                                                               | api.appstore.ai                      |

### Configuring Frontend

Next, configure the frontend.

Configuration File: `k8s/environments/production/aas-frontend-values.yaml`
| Field | Type | Description | Example |
| --------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| image.repository | string | Image to pull for frontend | registryname/ai-appstore/aas-frontend |
| image.tag | string | Image tag to pull | 1.10 |
| ingress.hosts[0].host | string | Hostname of frontend | web.appstore.ai |
| env.VUE_APP_BACKEND_URL | string | Hostname of backend so it can be accessed by the frontend | https://api.appstore.ai |

### Configuring Hosts

The front-end and back-end are served behind an Nginx Ingress Controller. Therefore, you will need to do the following:

- Configure the Helm Chart values to define the hostnames of the back-end and front-end
- Get the static IP address of the Nginx Ingress
- Configure DNS to redirect the URL of the frontend/backend to the ingress

#### Local Development

For local development, you can just add the hostnames that have been configured to your hosts file.

Run the following command: `sudo nano /etc/hosts`, and add the following

```
127.0.0.1    web.appstore.ai
127.0.0.1    api.appstore.ai
127.0.0.1    storage.appstore.ai
```

### Creating S3 Bucket

Based on the value of `env.PROD_MINIO_BUCKET_NAME`, you should create a bucket with that name in your S3 instance.

## Air-gapped Environment

In an environment without any access to the internet, some modifications need to be made.

### Transfering the Required Images

Firstly, the app will not be able to pull in images from the internet, and thus any docker images need to be available in the private registry of the cluster.

This includes:

- Main app images (backend, frontend)
- MongoDB images
- Emissary and/or KNative related images

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

### Transferring Helm Charts

Along with the images, you should also copy over the `k8s` folder to the machine that is connected to the air-gapped environment, to allow for installation. The machine connected needs to already have the [prerequisite tools](#prerequisite-tools) installed.

## Potential Issues

### Outdated Kubernetes Cluster

- If your K8S cluster is too old (< 1.20), the KNative backend for serving inference services will not work. As such, you have to use alternative backends such as the `emissary` backend. Note that other backends will not support auto-scaling from 0, meaning that the services will be always running and taking up resources on the cluster.
- We do currently have a manual-scaling option in the user interface as an alternative.

### HTTPS Certificates

If attempting to connected to a self hosted ClearML server using HTTPS (or any other service really), you will need to provide the TLS certificates needed to connect to it, otherwise the ClearML integration will not work.

This is supported by supplying the cert in the Helm chart values (for the backend Helm chart):

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

You will also need to configure the MongoDB Helm Chart as follows:

- Set `persistence.storageClass` to `aas-mongodb`

## Installing the Helm Charts

### Dependencies

#### Ingress Nginx

Before installing this, check if your cluster does not already have this installed by running `kubectl get ingressclass`

If you do not see `nginx`, then it likely means you need to install it as follows:

```bash
helm install ingress-nginx k8s/charts/dependencies/ingress-nginx
```

#### MongoDB

Assuming your MongoDB has been [properly configured](#mongodb-k8schartsdependenciesmongodb), install it as follows with Helm

```bash
helm install mongodb k8s/charts/dependencies/mongodb --namespace ai-appstore --values k8s/environments/production/mongodb-values.yaml
```

#### MinIO

If you need to set up MinIO, then install it as follows

```bash
helm install minio k8s/charts/dependencies/minio --namespace ai-appstore --values k8s/environments/production/minio-values.yaml
```

#### Emissary

##### CRDS

Install the CRDs first as follows

```bash
helm install emissary-crds k8s/charts/dependencies/emissary-crds --values k8s/environments/production/emissary-crd-values.yaml
```

##### Emissary

Then install Emissary

```bash
helm install emissary-ingress k8s/charts/dependencies/emissary-ingress --namespace emissary --create-namespace --values k8s/environments/production/emisary-values.yaml
```

#### KNative Serving

Install KNative Serving as follows:

```bash
helm install knative-serving k8s/charts/aas-knative-backend-private --namespace inference-engine --values k8s/environments/production/aas-knative-backend-values.yaml
```

### Installing the Main App

#### Front-End

Install the front-end as follows

```bash
helm install aas-frontend k8s/charts/aas-frontend --namespace ai-appstore --values k8s/environments/production/aas-frontend-values.yaml
```

#### Back-End

Install the backend as follows

```bash
helm install aas-backend k8s/charts/aas-backend --namespace ai-appstore --values k8s/environments/production/aas-backend-values.yaml
```

Note that you might also want to pass the CA certs needed to connect with ClearML (self hosted) here as well (see [here](#self-hosted-clearml)):

```bash

helm install aas-backend k8s/charts/aas-backend --namespace ai-appstore --values k8s/environments/production/aas-backend-values.yaml --set-file certs.CA_CERT=<path to cert file>
```

## Accessing the Application

Now, the AI App Store should be up and running. You should be able to access it by going to the hostname specified in your front-end Helm chart config (e.g `web.appstore.ai`)

To login, use the credentials specified in `env.PROD_FIRST_SUPERUSER_ID` and `env.PROD_FIRST_SUPERUSER_PASSWORD` to log in.

### Creating Other User Accounts

Once logged in as the first admin user, you can add more users through the [Admin Dashboard](../../user-guide/admin/accessing-admin-portal.md)
