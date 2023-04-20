# Deploy PCCS service on Kubernetes

PCCS (Provisioning Certificate Caching Service) service implementation comes from
[DCAP](https://github.com/intel/SGXDataCenterAttestationPrimitives/blob/master/QuoteGeneration/pccs/README.md).
On the local cluster of CSP, it can be deployed as a microservice on Kubernetes.

![](/doc/pccs-k8s.png)

## 1. Build Container

```
cd container
docker build -t <your registry> .
```

## 2. Install via Helm Chart

### 2.1 Create Kubernetes Secrets for PCCS SSL Key

The PCCS load the key and cert with name `private.pem` and `file.crt`,
we need rename the key to `private.pem` and cert to `file.crt` first,
and then create `Secret` in Kubernetes:

```Shell
kubectl create secret generic dcap-pccs-ssl --from-file=./private.pem --from-file=./file.crt -n dcap-pccs
```

### 2.2 Customize via `myvalues.yaml`

Customize your chart via `myvalues.yaml` like

```
image:
  repository: <your registry>/dcap-pccs

PCCSConfig:
  apiKey: <your API key>
  userToken: <your user Token>
  adminToken: <your admin Token>
  sslSecret: dcap-pccs-ssl
```

### 2.3 Helm install the DCAP PCCS Helm Chart

Clone the repo and use `helm install` to install DCAP PCCS to Kubernetes
cluster

```
cd chart
helm install -f myvalues.yaml -n dcap-pccs dcap-pccs .
```
