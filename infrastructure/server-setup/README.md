# Server Setup
This folder contains a basic cluster-setup you can use for the rag-template.

It includes a *terraform*  script that will create a basic kubernetes cluster, as well as a *helm* chart which will install the basics tools required on the cluster.

Due to a problem with the cert-manager helmchart the CRDs have to be manually installed:

```bash
helm repo add jetstack https://charts.jetstack.io
kubectl create ns <your namespace>
helm template cert-manager jetstack/cert-manager --namespace <your namespace> --set installCRDs=true | kubectl apply -f -

```
