# Deployment Guide - MCSP Scenario 1

This guide provides detailed instructions for deploying the SaaS Customer Portal application using the MCSP Scenario 1 architecture.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deploy CI/CD Pipeline](#deploy-cicd-pipeline)
4. [Configure GitOps](#configure-gitops)
5. [Setup Multi-Cluster Management](#setup-multi-cluster-management)
6. [Configure Certificate Management](#configure-certificate-management)
7. [Deploy Service Mesh](#deploy-service-mesh)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- OpenShift 4.12+ clusters (Hub + Managed clusters)
- `oc` CLI tool
- `kubectl` CLI tool
- `git` CLI tool
- Access to container registry (Quay.io or internal registry)

### Required Operators

Install the following operators on the Hub cluster:

```bash
# OpenShift Pipelines (Tekton)
oc apply -f https://raw.githubusercontent.com/openshift/pipelines-operator/master/deploy/operator.yaml

# OpenShift GitOps (ArgoCD)
oc apply -f https://raw.githubusercontent.com/redhat-developer/gitops-operator/master/deploy/operator.yaml

# Red Hat Advanced Cluster Management
# Install via OperatorHub in OpenShift Console

# cert-manager
oc apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Red Hat OpenShift Service Mesh (optional)
# Install via OperatorHub in OpenShift Console
```

### Access Requirements

- Cluster admin access to Hub cluster
- Admin access to managed clusters
- Git repository access (read/write)
- Container registry credentials

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mcsp-scenario1
```

### 2. Create Namespaces

```bash
# CI/CD namespace
oc create namespace saas-cicd

# Application namespaces
oc create namespace saas-app-dev
oc create namespace saas-app-staging
oc create namespace saas-app-prod

# GitOps namespace
oc create namespace saas-gitops
```

### 3. Configure Secrets

#### Git Credentials

```bash
# For HTTPS authentication
oc create secret generic git-credentials \
  --from-literal=username=<your-git-username> \
  --from-literal=password=<your-git-token> \
  -n saas-cicd

# Annotate for Tekton
oc annotate secret git-credentials \
  tekton.dev/git-0=https://github.com \
  -n saas-cicd

# For SSH authentication
oc create secret generic git-credentials \
  --from-file=ssh-privatekey=~/.ssh/id_rsa \
  --from-file=known_hosts=~/.ssh/known_hosts \
  --type=kubernetes.io/ssh-auth \
  -n saas-cicd
```

#### Container Registry Credentials

```bash
oc create secret docker-registry registry-credentials \
  --docker-server=quay.io \
  --docker-username=<your-username> \
  --docker-password=<your-password> \
  --docker-email=<your-email> \
  -n saas-cicd
```

#### Webhook Secret

```bash
oc create secret generic webhook-secret \
  --from-literal=secretToken=$(openssl rand -hex 20) \
  -n saas-cicd
```

## Deploy CI/CD Pipeline

### 1. Apply Pipeline Resources

```bash
# Service account and RBAC
oc apply -f pipelines/resources/pipeline-sa.yaml

# Pipeline tasks
oc apply -f pipelines/tasks/

# Main pipeline
oc apply -f pipelines/pipeline.yaml

# Triggers
oc apply -f pipelines/triggers/
```

### 2. Link Secrets to Service Account

```bash
oc secrets link pipeline-sa git-credentials -n saas-cicd
oc secrets link pipeline-sa registry-credentials -n saas-cicd
```

### 3. Get Webhook URL

```bash
# Get the route URL
WEBHOOK_URL=$(oc get route saas-app-webhook -n saas-cicd -o jsonpath='{.spec.host}')
echo "Webhook URL: https://${WEBHOOK_URL}"
```

### 4. Configure Git Webhook

In your Git repository settings:
- Add webhook URL: `https://${WEBHOOK_URL}`
- Content type: `application/json`
- Secret: Use the value from `webhook-secret`
- Events: Push events, Pull request events

### 5. Test Pipeline

```bash
# Trigger a manual pipeline run
oc create -f pipelines/pipeline.yaml
```

## Configure GitOps

### 1. Deploy ArgoCD Applications

```bash
# Apply ArgoCD applications
oc apply -f gitops/applications/saas-app.yaml

# For multi-cluster deployment
oc apply -f gitops/applications/saas-app-set.yaml
```

### 2. Access ArgoCD UI

```bash
# Get ArgoCD route
ARGOCD_URL=$(oc get route openshift-gitops-server -n openshift-gitops -o jsonpath='{.spec.host}')
echo "ArgoCD URL: https://${ARGOCD_URL}"

# Get admin password
ARGOCD_PASSWORD=$(oc get secret openshift-gitops-cluster -n openshift-gitops -o jsonpath='{.data.admin\.password}' | base64 -d)
echo "Admin Password: ${ARGOCD_PASSWORD}"
```

### 3. Sync Applications

```bash
# Sync dev environment
argocd app sync saas-customer-portal-dev

# Sync staging environment
argocd app sync saas-customer-portal-staging

# Production requires manual sync
argocd app sync saas-customer-portal-production
```

## Setup Multi-Cluster Management

### 1. Import Managed Clusters

```bash
# Apply managed cluster definitions
oc apply -f rhacm/managedcluster/cluster-labels.yaml
```

### 2. Configure Placement Rules

```bash
# Apply placement rules
oc apply -f rhacm/placement/placement.yaml
oc apply -f rhacm/placement/placement-binding.yaml
```

### 3. Apply Policies

```bash
# Security policies
oc apply -f rhacm/policies/security-policy.yaml

# Resource policies
oc apply -f rhacm/policies/resource-policy.yaml
```

### 4. Verify Cluster Status

```bash
# Check managed clusters
oc get managedclusters

# Check placement decisions
oc get placementdecisions -n open-cluster-management

# Check policy compliance
oc get policies -n open-cluster-management
```

## Configure Certificate Management

### 1. Deploy cert-manager Issuers

```bash
# Apply cluster issuers
oc apply -f cert-manager/issuer.yaml
```

### 2. Create Certificates

```bash
# Apply certificate requests
oc apply -f cert-manager/certificate.yaml
```

### 3. Verify Certificates

```bash
# Check certificate status
oc get certificates -n saas-app-prod
oc get certificates -n saas-app-staging
oc get certificates -n saas-app-dev

# Describe certificate for details
oc describe certificate saas-customer-portal-tls -n saas-app-prod
```

## Deploy Service Mesh

### 1. Create Service Mesh Control Plane

```bash
# Create istio-system namespace
oc create namespace istio-system

# Apply Service Mesh Control Plane (create this file based on your needs)
oc apply -f - <<EOF
apiVersion: maistra.io/v2
kind: ServiceMeshControlPlane
metadata:
  name: basic
  namespace: istio-system
spec:
  version: v2.4
  tracing:
    type: Jaeger
  addons:
    grafana:
      enabled: true
    kiali:
      enabled: true
    prometheus:
      enabled: true
EOF
```

### 2. Create Service Mesh Member Roll

```bash
oc apply -f - <<EOF
apiVersion: maistra.io/v1
kind: ServiceMeshMemberRoll
metadata:
  name: default
  namespace: istio-system
spec:
  members:
    - saas-app-dev
    - saas-app-staging
    - saas-app-prod
EOF
```

### 3. Apply Service Mesh Configurations

```bash
# Apply gateway
oc apply -f service-mesh/gateway.yaml

# Apply virtual service
oc apply -f service-mesh/virtual-service.yaml

# Apply destination rules
oc apply -f service-mesh/destination-rule.yaml

# Apply security policies
oc apply -f service-mesh/peer-authentication.yaml
```

### 4. Enable Sidecar Injection

```bash
# Label namespaces for automatic sidecar injection
oc label namespace saas-app-prod istio-injection=enabled
oc label namespace saas-app-staging istio-injection=enabled
oc label namespace saas-app-dev istio-injection=enabled
```

## Verification

### 1. Verify Pipeline

```bash
# Check pipeline runs
oc get pipelineruns -n saas-cicd

# View pipeline logs
tkn pipelinerun logs <pipelinerun-name> -n saas-cicd -f
```

### 2. Verify GitOps Deployment

```bash
# Check ArgoCD application status
oc get applications -n openshift-gitops

# Check application pods
oc get pods -n saas-app-dev
oc get pods -n saas-app-staging
oc get pods -n saas-app-prod
```

### 3. Verify Application Access

```bash
# Get application routes
oc get routes -n saas-app-dev
oc get routes -n saas-app-staging
oc get routes -n saas-app-prod

# Test health endpoint
curl https://<route-url>/health
```

### 4. Verify Service Mesh

```bash
# Check Istio components
oc get pods -n istio-system

# Access Kiali dashboard
oc get route kiali -n istio-system -o jsonpath='{.spec.host}'

# Check virtual services
oc get virtualservices -n saas-app-prod
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

1. Configure monitoring and alerting
2. Setup backup and disaster recovery
3. Implement observability with distributed tracing
4. Configure autoscaling policies
5. Setup cost management and optimization

## Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [OpenShift Documentation](https://docs.openshift.com/)
- [RHACM Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/)