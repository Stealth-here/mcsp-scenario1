# MCSP Scenario 1: Multi-Cluster SaaS Platform

This project demonstrates a complete Multi-Cluster SaaS Platform (MCSP) implementation using Red Hat OpenShift, showcasing Scenario 1 architecture with automated CI/CD pipelines, GitOps deployment, and multi-cluster management.

## Overview

This repository contains a sample SaaS application (`saas-customer-portal`) with complete infrastructure-as-code for:
- **CI/CD Pipeline**: Tekton pipelines for automated build, test, and deployment
- **GitOps**: ArgoCD-based declarative deployment across multiple environments
- **Multi-Cluster Management**: Red Hat Advanced Cluster Management (RHACM) for cluster orchestration
- **Security**: Automated certificate management with cert-manager
- **Service Mesh**: Istio for advanced traffic management and observability

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Hub Cluster                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Tekton     │  │   ArgoCD     │  │    RHACM     │          │
│  │  Pipelines   │  │   GitOps     │  │  Management  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Manages & Deploys
                              ▼
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                     ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Dev Cluster  │      │ Staging      │      │ Production   │
│              │      │ Cluster      │      │ Cluster      │
│ saas-app     │      │ saas-app     │      │ saas-app     │
└──────────────┘      └──────────────┘      └──────────────┘
```

## Prerequisites

- OpenShift 4.12+ clusters (Hub + Managed clusters)
- Red Hat Advanced Cluster Management (RHACM) 2.8+
- OpenShift GitOps (ArgoCD) operator
- OpenShift Pipelines (Tekton) operator
- cert-manager operator
- Red Hat OpenShift Service Mesh (optional)
- Container registry access (Quay.io or internal registry)
- Git repository for GitOps manifests

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mcsp-scenario1
```

### 2. Install Required Operators

```bash
# Install OpenShift Pipelines
oc apply -f https://raw.githubusercontent.com/openshift/pipelines-operator/master/deploy/operator.yaml

# Install OpenShift GitOps
oc apply -f https://raw.githubusercontent.com/redhat-developer/gitops-operator/master/deploy/operator.yaml

# Install cert-manager
oc apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 3. Configure Pipeline Secrets

```bash
# Create namespace
oc create namespace saas-cicd

# Configure Git and registry credentials
oc create secret generic git-credentials \
  --from-literal=username=<git-username> \
  --from-literal=password=<git-token> \
  -n saas-cicd

oc create secret docker-registry registry-credentials \
  --docker-server=quay.io \
  --docker-username=<registry-username> \
  --docker-password=<registry-password> \
  -n saas-cicd
```

### 4. Deploy Tekton Pipeline

```bash
# Apply pipeline resources
oc apply -f pipelines/resources/ -n saas-cicd
oc apply -f pipelines/tasks/ -n saas-cicd
oc apply -f pipelines/pipeline.yaml -n saas-cicd
oc apply -f pipelines/triggers/ -n saas-cicd
```

### 5. Configure ArgoCD Applications

```bash
# Create GitOps namespace
oc create namespace saas-gitops

# Deploy ArgoCD applications
oc apply -f gitops/applications/ -n saas-gitops
```

### 6. Configure RHACM Policies

```bash
# Apply placement rules and policies
oc apply -f rhacm/placement/ -n open-cluster-management
oc apply -f rhacm/policies/ -n open-cluster-management
```

## Project Structure

```
mcsp-scenario1/
├── app/                    # Sample SaaS application
├── pipelines/              # Tekton CI/CD pipelines
├── gitops/                 # ArgoCD GitOps configurations
├── rhacm/                  # RHACM multi-cluster management
├── cert-manager/           # Certificate management
├── service-mesh/           # Istio service mesh configs
└── docs/                   # Documentation
```

## Application Endpoints

Once deployed, the application exposes:

- **Health Check**: `GET /health`
- **Application Info**: `GET /info`
- **Items API**: 
  - `GET /api/items` - List all items
  - `POST /api/items` - Create new item
  - `GET /api/items/<id>` - Get specific item
  - `PUT /api/items/<id>` - Update item
  - `DELETE /api/items/<id>` - Delete item
- **Metrics**: `GET /metrics` - Prometheus metrics

## Environment Configuration

The application supports multiple environments through Kustomize overlays:

- **Development**: `gitops/overlays/dev/`
- **Staging**: `gitops/overlays/staging/`
- **Production**: `gitops/overlays/production/`

Each environment has specific configurations for:
- Replica counts
- Resource limits
- Environment variables
- TLS certificates
- Ingress/Route configurations

## CI/CD Pipeline Flow

1. **Git Clone**: Clone source code from repository
2. **Build Image**: Build container image using Dockerfile
3. **Run Tests**: Execute unit and integration tests
4. **Security Scan**: Scan for vulnerabilities using Trivy
5. **Push Image**: Push to container registry
6. **Update GitOps**: Update image tag in GitOps repository
7. **ArgoCD Sync**: Automatic deployment to target clusters

## Multi-Cluster Deployment

RHACM manages deployments across multiple clusters using:

- **Placement Rules**: Define which clusters receive deployments
- **ApplicationSets**: Manage multiple ArgoCD applications
- **Policies**: Enforce security and compliance requirements
- **Cluster Labels**: Target specific cluster groups

Example cluster labels:
```yaml
environment: production
region: us-east-1
tier: premium
```

## Security Features

- **TLS Certificates**: Automated certificate management with Let's Encrypt
- **Image Scanning**: Vulnerability scanning in CI pipeline
- **Network Policies**: Restrict pod-to-pod communication
- **RBAC**: Role-based access control
- **Secret Management**: Encrypted secrets with Sealed Secrets
- **mTLS**: Service-to-service encryption with Istio

## Monitoring and Observability

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Jaeger**: Distributed tracing (with Service Mesh)
- **Kiali**: Service mesh observability
- **OpenShift Logging**: Centralized log aggregation

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Detailed deployment instructions
- [Architecture](docs/ARCHITECTURE.md) - Architecture deep dive
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and fixes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache License 2.0

## Support

For issues and questions:
- Open an issue in the repository
- Contact the platform team
- Check the documentation in `docs/`

## References

- [Red Hat OpenShift Documentation](https://docs.openshift.com/)
- [Red Hat Advanced Cluster Management](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/)
- [OpenShift GitOps](https://docs.openshift.com/container-platform/latest/cicd/gitops/understanding-openshift-gitops.html)
- [OpenShift Pipelines](https://docs.openshift.com/container-platform/latest/cicd/pipelines/understanding-openshift-pipelines.html)