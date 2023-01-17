# Deployment of the AI Appstore on a K8S Cluster

## Configuring Helm Charts

## Air-gapped Environment

### Transfering the Required Images

### Pushing to the Private Registry

### Using Privately Hosted Images

## Potential Issues

### Storage Provisioning

- It is possible that the K8S cluster may lack a dynamic storage provisioner.
- To check, run the following command: `kubectl get sc -A`. If no resources were found, it means you don't have a storage provisioner configured.
- This is problematic as MongoDB requires a persistent volume to persist it's data
- ## To solve this, you need to manually provision storage as follows:
