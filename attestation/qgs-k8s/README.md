# Deploy QGS service on Kubernetes

QGS (Quote Generation Service) implementation comes from
[DCAP](https://github.com/intel/SGXDataCenterAttestationPrimitives/tree/master/QuoteGeneration/quote_wrapper/qgs).
It should run a copy in all TDX hosts to handle requests from TD VMs.
On the local cluster of CSP, it can be deployed as a microservice via `DaemonSet`
on Kubernetes.

![](/doc/qgs-k8s.png)

## 1. Build Container

```
cd container
docker build -t <your registry> .
```

## 2. Install via Helm Chart

### 2.1 Customize via `myvalues.yaml`

Customize your chart via `myvalues.yaml` like

```
image:
  repository: <your registry>/tdx-qgs
```

### 2.2 Helm install the TDX QGS Helm Chart

Clone the repo and use `helm install` to install TDX QGS to Kubernetes
cluster

```
cd chart
helm install -f myvalues.yaml -n tdx-qgs tdx-qgs .
```
