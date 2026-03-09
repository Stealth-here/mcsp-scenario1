# 🚀 Complete Step-by-Step Deployment Guide - MCSP Scenario 1

This comprehensive guide will walk you through every single step needed to deploy the Multi-Cluster SaaS Platform (MCSP) Scenario 1 implementation. Follow each step carefully and verify your progress along the way.

## 📋 Table of Contents

1. [Prerequisites Checklist](#1-prerequisites-checklist)
2. [Step 1: Initial Setup](#2-step-1-initial-setup)
3. [Step 2: Configure Secrets and Credentials](#3-step-2-configure-secrets-and-credentials)
4. [Step 3: Update Configuration Files](#4-step-3-update-configuration-files)
5. [Step 4: Install Required Operators](#5-step-4-install-required-operators)
6. [Step 5: Deploy Pipeline Infrastructure](#6-step-5-deploy-pipeline-infrastructure)
7. [Step 6: Configure GitOps (ArgoCD)](#7-step-6-configure-gitops-argocd)
8. [Step 7: Configure RHACM](#8-step-7-configure-rhacm)
9. [Step 8: Configure Cert Manager](#9-step-8-configure-cert-manager)
10. [Step 9: Configure Service Mesh (Optional)](#10-step-9-configure-service-mesh-optional)
11. [Step 10: Trigger First Deployment](#11-step-10-trigger-first-deployment)
12. [Step 11: Verify Complete Workflow](#12-step-11-verify-complete-workflow)
13. [Step 12: Setup Webhook for Automated Deployments](#13-step-12-setup-webhook-for-automated-deployments)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Prerequisites Checklist

Before starting, ensure you have all the following requirements:

### 1.1 OpenShift Cluster Requirements

- [ ] **OpenShift 4.12 or higher** installed and running
- [ ] **Hub Cluster**: One cluster for CI/CD, GitOps, and RHACM management
- [ ] **Managed Clusters** (optional but recommended): Separate clusters for dev, staging, and production
- [ ] **Cluster Admin Access**: You need cluster-admin privileges on all clusters
- [ ] **Cluster Resources**: Minimum 16 vCPU, 32GB RAM per cluster

### 1.2 Required CLI Tools

Install the following tools on your local machine:

#### OpenShift CLI (oc)
```bash
# macOS
brew install openshift-cli

# Linux
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xvf openshift-client-linux.tar.gz
sudo mv oc kubectl /usr/local/bin/

# Verify installation
oc version
```

#### Kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

#### Git
```bash
# macOS
brew install git

# Linux
sudo yum install git -y  # RHEL/CentOS
sudo apt-get install git -y  # Ubuntu/Debian

# Verify installation
git --version
```

#### Tekton CLI (tkn)
```bash
# macOS
brew install tektoncd-cli

# Linux
wget https://github.com/tektoncd/cli/releases/download/v0.32.0/tkn_0.32.0_Linux_x86_64.tar.gz
tar -xvf tkn_0.32.0_Linux_x86_64.tar.gz
sudo mv tkn /usr/local/bin/

# Verify installation
tkn version
```

#### ArgoCD CLI
```bash
# macOS
brew install argocd

# Linux
wget https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd-linux-amd64
sudo mv argocd-linux-amd64 /usr/local/bin/argocd

# Verify installation
argocd version --client
```

### 1.3 Access Requirements

- [ ] **Container Registry Access**: Quay.io, Docker Hub, or internal registry
  - Registry URL (e.g., `quay.io`)
  - Username
  - Password/Token
  - Email address

- [ ] **Git Repository Access**: GitHub, GitLab, or Bitbucket
  - Repository URL
  - Username
  - Personal Access Token (PAT) or SSH key
  - Write permissions to the repository

- [ ] **Domain/DNS Access** (for production):
  - Domain name for your application
  - Ability to create DNS records
  - SSL/TLS certificate authority access (or use Let's Encrypt)

### 1.4 Network Requirements

- [ ] Internet access from OpenShift clusters
- [ ] Access to container registries (quay.io, docker.io, etc.)
- [ ] Access to Git repositories
- [ ] Firewall rules allowing webhook callbacks (for automated deployments)

### 1.5 Knowledge Prerequisites

- [ ] Basic understanding of Kubernetes/OpenShift
- [ ] Familiarity with Git and GitOps concepts
- [ ] Basic YAML syntax knowledge
- [ ] Command-line interface experience

**✅ Verification:**
```bash
# Verify you can access your OpenShift cluster
oc login <YOUR_CLUSTER_URL> --token=<YOUR_TOKEN>
oc whoami
# Expected output: Your username

# Check cluster version
oc version
# Expected output: OpenShift version 4.12 or higher
```

---

## 2. Step 1: Initial Setup

### 2.1 Navigate to Your Workspace

```bash
cd /Users/likithrdevanga/Desktop
```

### 2.2 Clone or Navigate to the Project

If you already have the project:
```bash
cd mcsp-scenario1
```

If you need to clone it:
```bash
git clone <YOUR_REPOSITORY_URL>
cd mcsp-scenario1
```

### 2.3 Initialize Git Repository (if not already initialized)

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial MCSP Scenario 1 implementation"
```

### 2.4 Create Remote Repository

1. Go to GitHub/GitLab and create a new repository named `mcsp-scenario1`
2. **Do not** initialize with README, .gitignore, or license (we already have these)

### 2.5 Link Local Repository to Remote

```bash
# Replace <YOUR_GITHUB_USERNAME> with your actual username
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git

# Verify remote
git remote -v
# Expected output:
# origin  https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git (fetch)
# origin  https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git (push)
```

### 2.6 Create Branch Structure

```bash
# Create and push main branch
git branch -M main
git push -u origin main

# Create development branch
git checkout -b develop
git push -u origin develop

# Return to main branch
git checkout main
```

**✅ Verification:**
```bash
git branch -a
# Expected output:
# * main
#   develop
#   remotes/origin/main
#   remotes/origin/develop
```

### 2.7 Login to OpenShift Cluster

```bash
# Get your login command from OpenShift Console:
# Click your username (top right) → Copy login command → Display Token

oc login --token=<YOUR_TOKEN> --server=<YOUR_CLUSTER_API_URL>

# Example:
# oc login --token=sha256~abc123... --server=https://api.cluster.example.com:6443
```

**✅ Verification:**
```bash
oc whoami
# Expected output: Your username

oc cluster-info
# Expected output: Cluster information including API server URL
```

---

## 3. Step 2: Configure Secrets and Credentials

### 3.1 Create Required Namespaces

```bash
# Create CI/CD namespace
oc create namespace saas-cicd

# Create application namespaces
oc create namespace saas-app-dev
oc create namespace saas-app-staging
oc create namespace saas-app-prod

# Create GitOps namespace (if not auto-created by operator)
oc create namespace saas-gitops
```

**✅ Verification:**
```bash
oc get namespaces | grep saas
# Expected output:
# saas-cicd          Active   1m
# saas-app-dev       Active   1m
# saas-app-staging   Active   1m
# saas-app-prod      Active   1m
# saas-gitops        Active   1m
```

### 3.2 Create Git Credentials Secret

#### Option A: HTTPS Authentication (Recommended for GitHub/GitLab)

First, create a Personal Access Token:
- **GitHub**: Settings → Developer settings → Personal access tokens → Generate new token
  - Required scopes: `repo` (full control of private repositories)
- **GitLab**: Settings → Access Tokens → Add new token
  - Required scopes: `api`, `read_repository`, `write_repository`

```bash
# Replace placeholders with your actual credentials
export GIT_USERNAME="<YOUR_GITHUB_USERNAME>"
export GIT_TOKEN="<YOUR_PERSONAL_ACCESS_TOKEN>"

# Create the secret
oc create secret generic git-credentials \
  --from-literal=username=${GIT_USERNAME} \
  --from-literal=password=${GIT_TOKEN} \
  -n saas-cicd

# Annotate for Tekton to use with GitHub
oc annotate secret git-credentials \
  tekton.dev/git-0=https://github.com \
  -n saas-cicd

# For GitLab, use:
# oc annotate secret git-credentials \
#   tekton.dev/git-0=https://gitlab.com \
#   -n saas-cicd
```

#### Option B: SSH Authentication

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/mcsp_deploy_key

# Add public key to GitHub/GitLab:
# GitHub: Settings → SSH and GPG keys → New SSH key
# GitLab: Settings → SSH Keys → Add new key
cat ~/.ssh/mcsp_deploy_key.pub

# Create the secret
oc create secret generic git-credentials \
  --from-file=ssh-privatekey=~/.ssh/mcsp_deploy_key \
  --from-file=known_hosts=~/.ssh/known_hosts \
  --type=kubernetes.io/ssh-auth \
  -n saas-cicd

# If known_hosts doesn't exist, create it:
ssh-keyscan github.com >> ~/.ssh/known_hosts
# or for GitLab:
# ssh-keyscan gitlab.com >> ~/.ssh/known_hosts
```

**✅ Verification:**
```bash
oc get secret git-credentials -n saas-cicd
# Expected output:
# NAME              TYPE                              DATA   AGE
# git-credentials   kubernetes.io/basic-auth          2      1m
```

### 3.3 Create Container Registry Credentials

#### For Quay.io:

1. Create a Quay.io account at https://quay.io
2. Create a robot account or use your credentials
3. Create a repository named `saas-customer-portal`

```bash
# Replace placeholders with your actual credentials
export REGISTRY_SERVER="quay.io"
export REGISTRY_USERNAME="<YOUR_QUAY_USERNAME>"
export REGISTRY_PASSWORD="<YOUR_QUAY_PASSWORD>"
export REGISTRY_EMAIL="<YOUR_EMAIL>"

# Create the secret
oc create secret docker-registry registry-credentials \
  --docker-server=${REGISTRY_SERVER} \
  --docker-username=${REGISTRY_USERNAME} \
  --docker-password=${REGISTRY_PASSWORD} \
  --docker-email=${REGISTRY_EMAIL} \
  -n saas-cicd
```

#### For Docker Hub:

```bash
export REGISTRY_SERVER="docker.io"
export REGISTRY_USERNAME="<YOUR_DOCKERHUB_USERNAME>"
export REGISTRY_PASSWORD="<YOUR_DOCKERHUB_PASSWORD>"
export REGISTRY_EMAIL="<YOUR_EMAIL>"

oc create secret docker-registry registry-credentials \
  --docker-server=${REGISTRY_SERVER} \
  --docker-username=${REGISTRY_USERNAME} \
  --docker-password=${REGISTRY_PASSWORD} \
  --docker-email=${REGISTRY_EMAIL} \
  -n saas-cicd
```

#### For OpenShift Internal Registry:

```bash
# Get internal registry URL
INTERNAL_REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')

# Create secret using your OpenShift token
oc create secret docker-registry registry-credentials \
  --docker-server=${INTERNAL_REGISTRY} \
  --docker-username=$(oc whoami) \
  --docker-password=$(oc whoami -t) \
  -n saas-cicd
```

**✅ Verification:**
```bash
oc get secret registry-credentials -n saas-cicd
# Expected output:
# NAME                   TYPE                             DATA   AGE
# registry-credentials   kubernetes.io/dockerconfigjson   1      1m
```

### 3.4 Create Webhook Secret

```bash
# Generate a random secret token
export WEBHOOK_SECRET=$(openssl rand -hex 20)

# Save this token - you'll need it later for webhook configuration
echo "Webhook Secret: ${WEBHOOK_SECRET}"
echo "${WEBHOOK_SECRET}" > webhook-secret.txt

# Create the secret
oc create secret generic webhook-secret \
  --from-literal=secretToken=${WEBHOOK_SECRET} \
  -n saas-cicd
```

**✅ Verification:**
```bash
oc get secret webhook-secret -n saas-cicd
# Expected output:
# NAME             TYPE     DATA   AGE
# webhook-secret   Opaque   1      1m

# Verify the secret value
oc get secret webhook-secret -n saas-cicd -o jsonpath='{.data.secretToken}' | base64 -d
# Expected output: Your webhook secret token
```

### 3.5 Understanding Base64 Encoding

If you need to manually encode secrets:

```bash
# Encode a string to base64
echo -n "my-secret-value" | base64
# Output: bXktc2VjcmV0LXZhbHVl

# Decode a base64 string
echo "bXktc2VjcmV0LXZhbHVl" | base64 -d
# Output: my-secret-value

# Encode username:password for Docker auth
echo -n "username:password" | base64
```

### 3.6 Create ArgoCD Credentials (Optional)

Only needed if you want to interact with ArgoCD API directly:

```bash
# Wait until ArgoCD is installed (Step 6), then:
# Get ArgoCD admin password
ARGOCD_PASSWORD=$(oc get secret openshift-gitops-cluster -n openshift-gitops -o jsonpath='{.data.admin\.password}' | base64 -d)

# Create ArgoCD credentials secret
oc create secret generic argocd-credentials \
  --from-literal=server=openshift-gitops-server.openshift-gitops.svc.cluster.local \
  --from-literal=username=admin \
  --from-literal=password=${ARGOCD_PASSWORD} \
  -n saas-cicd
```

**📝 Important Notes:**
- Keep your secrets secure and never commit them to Git
- Store the webhook secret safely - you'll need it for Step 12
- If using a private container registry, ensure it's accessible from your cluster

---

## 4. Step 3: Update Configuration Files

Now we need to customize the configuration files with your specific values.

### 4.1 Update Pipeline Configuration

Edit `pipelines/pipeline.yaml`:

```bash
# Open the file in your editor
vi pipelines/pipeline.yaml
# or
nano pipelines/pipeline.yaml
```

Update the following default values:

```yaml
# Line 17: Update Git repository URL
git-url:
  default: https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git

# Line 27: Update image name with your registry
image-name:
  default: quay.io/<YOUR_QUAY_USERNAME>/saas-customer-portal
  # or for Docker Hub:
  # default: docker.io/<YOUR_DOCKERHUB_USERNAME>/saas-customer-portal

# Line 47: Update GitOps repository URL (same as git-url if using same repo)
gitops-repo-url:
  default: https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git
```

**Quick sed command to update (replace placeholders first):**
```bash
# Set your values
export GITHUB_USER="<YOUR_GITHUB_USERNAME>"
export QUAY_USER="<YOUR_QUAY_USERNAME>"

# Update git-url
sed -i.bak "s|https://github.com/example/saas-customer-portal.git|https://github.com/${GITHUB_USER}/mcsp-scenario1.git|g" pipelines/pipeline.yaml

# Update image-name
sed -i.bak "s|quay.io/mcsp/saas-customer-portal|quay.io/${QUAY_USER}/saas-customer-portal|g" pipelines/pipeline.yaml

# Update gitops-repo-url
sed -i.bak "s|https://github.com/example/saas-gitops.git|https://github.com/${GITHUB_USER}/mcsp-scenario1.git|g" pipelines/pipeline.yaml
```

### 4.2 Update ArgoCD Application Configuration

Edit `gitops/applications/saas-app.yaml`:

```bash
vi gitops/applications/saas-app.yaml
```

Update the repository URL in all three applications (dev, staging, production):

```yaml
# Lines 18, 68, 114: Update repoURL
repoURL: https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git
```

**Quick sed command:**
```bash
sed -i.bak "s|https://github.com/example/saas-gitops.git|https://github.com/${GITHUB_USER}/mcsp-scenario1.git|g" gitops/applications/saas-app.yaml
```

### 4.3 Update ArgoCD ApplicationSet Configuration

Edit `gitops/applications/saas-app-set.yaml`:

```bash
vi gitops/applications/saas-app-set.yaml
```

Update the repository URL:

```yaml
# Update repoURL
repoURL: https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git
```

**Quick sed command:**
```bash
sed -i.bak "s|https://github.com/example/saas-gitops.git|https://github.com/${GITHUB_USER}/mcsp-scenario1.git|g" gitops/applications/saas-app-set.yaml
```

### 4.4 Update Deployment Image References

Edit deployment patches for each environment:

```bash
# Dev environment
vi gitops/overlays/dev/deployment-patch.yaml

# Staging environment
vi gitops/overlays/staging/deployment-patch.yaml

# Production environment
vi gitops/overlays/production/deployment-patch.yaml
```

Update the image reference in each file:

```yaml
# Update image
image: quay.io/<YOUR_QUAY_USERNAME>/saas-customer-portal:latest
```

**Quick sed command for all environments:**
```bash
find gitops/overlays -name "deployment-patch.yaml" -exec sed -i.bak "s|quay.io/mcsp/saas-customer-portal|quay.io/${QUAY_USER}/saas-customer-portal|g" {} \;
```

### 4.5 Update Route/Ingress Hostnames (Optional)

If you have a custom domain, update the route configurations:

```bash
vi gitops/base/route.yaml
```

Update the host field:

```yaml
spec:
  host: saas-customer-portal.<YOUR_DOMAIN>
```

### 4.6 Update Certificate Issuer (for Production)

Edit `cert-manager/issuer.yaml`:

```bash
vi cert-manager/issuer.yaml
```

Update the email address for Let's Encrypt:

```yaml
spec:
  acme:
    email: <YOUR_EMAIL>@example.com
```

### 4.7 Commit Configuration Changes

```bash
# Check what files were modified
git status

# Add all modified files
git add .

# Commit changes
git commit -m "Update configuration with custom values"

# Push to remote repository
git push origin main
```

**✅ Verification:**
```bash
# Verify all placeholders are replaced
grep -r "example" pipelines/ gitops/ cert-manager/ || echo "No 'example' placeholders found - Good!"
grep -r "<YOUR" pipelines/ gitops/ cert-manager/ || echo "No placeholder tags found - Good!"

# Verify your username is in the files
grep -r "${GITHUB_USER}" pipelines/pipeline.yaml gitops/applications/
# Expected output: Should show your username in multiple files
```

**📝 Important Notes:**
- Always use your actual registry where you have push permissions
- Ensure your Git repository URL is correct and accessible
- Keep backup files (*.bak) until you verify everything works
- Double-check that no placeholder values remain

---

## 5. Step 4: Install Required Operators

Operators provide the core functionality for our platform. We'll install them through the OpenShift OperatorHub.

### 5.1 Install OpenShift Pipelines Operator

#### Via OpenShift Console:

1. Login to OpenShift Console: `https://console-openshift-console.apps.<YOUR_CLUSTER_DOMAIN>`
2. Navigate to: **Operators** → **OperatorHub**
3. Search for: **"Red Hat OpenShift Pipelines"**
4. Click on the operator tile
5. Click **Install**
6. Keep default settings:
   - **Update Channel**: `latest` or `pipelines-1.12`
   - **Installation Mode**: `All namespaces on the cluster`
   - **Installed Namespace**: `openshift-operators`
   - **Update approval**: `Automatic`
7. Click **Install**
8. Wait for installation to complete (Status: "Succeeded")

#### Via CLI:

```bash
# Create subscription
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-pipelines-operator
  namespace: openshift-operators
spec:
  channel: latest
  name: openshift-pipelines-operator-rh
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**✅ Verification:**
```bash
# Check operator installation
oc get csv -n openshift-operators | grep pipelines
# Expected output: openshift-pipelines-operator...   Succeeded

# Check if Tekton components are running
oc get pods -n openshift-pipelines
# Expected output: Multiple pods in Running state

# Verify Tekton version
tkn version
# Expected output: Client and Pipeline version information
```

**⚠️ Troubleshooting:**
If installation fails:
```bash
# Check operator pod logs
oc logs -n openshift-operators -l name=openshift-pipelines-operator

# Check subscription status
oc describe subscription openshift-pipelines-operator -n openshift-operators
```

### 5.2 Install OpenShift GitOps Operator

#### Via OpenShift Console:

1. Navigate to: **Operators** → **OperatorHub**
2. Search for: **"Red Hat OpenShift GitOps"**
3. Click on the operator tile
4. Click **Install**
5. Settings:
   - **Update Channel**: `latest` or `gitops-1.10`
   - **Installation Mode**: `All namespaces on the cluster`
   - **Installed Namespace**: `openshift-operators`
   - **Update approval**: `Automatic`
6. Click **Install**
7. Wait for installation (Status: "Succeeded")

#### Via CLI:

```bash
# Create subscription
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-gitops-operator
  namespace: openshift-operators
spec:
  channel: latest
  name: openshift-gitops-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**✅ Verification:**
```bash
# Check operator installation
oc get csv -n openshift-operators | grep gitops
# Expected output: openshift-gitops-operator...   Succeeded

# Check ArgoCD instance
oc get argocd -n openshift-gitops
# Expected output: 
# NAME                  AGE
# openshift-gitops      2m

# Check ArgoCD pods
oc get pods -n openshift-gitops
# Expected output: Multiple ArgoCD pods in Running state

# Get ArgoCD URL
oc get route openshift-gitops-server -n openshift-gitops -o jsonpath='{.spec.host}'
# Expected output: ArgoCD server URL
```

**⚠️ Troubleshooting:**
```bash
# If ArgoCD instance not created automatically
oc get argocd -n openshift-gitops

# Check operator logs
oc logs -n openshift-operators -l control-plane=gitops-operator

# Manually create ArgoCD instance if needed
cat <<EOF | oc apply -f -
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: openshift-gitops
  namespace: openshift-gitops
spec:
  server:
    route:
      enabled: true
EOF
```

### 5.3 Install cert-manager Operator

#### Via OpenShift Console:

1. Navigate to: **Operators** → **OperatorHub**
2. Search for: **"cert-manager Operator for Red Hat OpenShift"**
3. Click on the operator tile
4. Click **Install**
5. Settings:
   - **Update Channel**: `stable`
   - **Installation Mode**: `All namespaces on the cluster`
   - **Installed Namespace**: `openshift-operators`
   - **Update approval**: `Automatic`
6. Click **Install**
7. Wait for installation

#### Via CLI:

```bash
# Create subscription
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-cert-manager-operator
  namespace: openshift-operators
spec:
  channel: stable-v1
  name: openshift-cert-manager-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**✅ Verification:**
```bash
# Check operator installation
oc get csv -n openshift-operators | grep cert-manager
# Expected output: cert-manager-operator...   Succeeded

# Check cert-manager pods
oc get pods -n cert-manager
# Expected output: cert-manager pods in Running state

# Verify cert-manager API
oc api-resources | grep cert-manager
# Expected output: Multiple cert-manager resources listed
```

### 5.4 Install Red Hat Advanced Cluster Management (RHACM)

**📝 Note:** RHACM requires a separate license and significant resources. Skip this if you're doing a single-cluster deployment.

#### Via OpenShift Console:

1. Navigate to: **Operators** → **OperatorHub**
2. Search for: **"Advanced Cluster Management for Kubernetes"**
3. Click on the operator tile
4. Click **Install**
5. Settings:
   - **Update Channel**: `release-2.9`
   - **Installation Mode**: `All namespaces on the cluster`
   - **Installed Namespace**: `openshift-operators`
   - **Update approval**: `Automatic`
6. Click **Install**
7. Wait for installation (this takes 5-10 minutes)

#### Via CLI:

```bash
# Create namespace
oc create namespace open-cluster-management

# Create subscription
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: advanced-cluster-management
  namespace: open-cluster-management
spec:
  channel: release-2.9
  name: advanced-cluster-management
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

#### Create MultiClusterHub Instance:

```bash
# Wait for operator to be ready
oc wait --for=condition=Ready subscription/advanced-cluster-management -n open-cluster-management --timeout=300s

# Create MultiClusterHub
cat <<EOF | oc apply -f -
apiVersion: operator.open-cluster-management.io/v1
kind: MultiClusterHub
metadata:
  name: multiclusterhub
  namespace: open-cluster-management
spec: {}
EOF
```

**✅ Verification:**
```bash
# Check operator installation
oc get csv -n open-cluster-management | grep advanced-cluster-management
# Expected output: advanced-cluster-management...   Succeeded

# Check MultiClusterHub status
oc get multiclusterhub -n open-cluster-management
# Expected output: 
# NAME              STATUS    AGE
# multiclusterhub   Running   5m

# Check RHACM pods
oc get pods -n open-cluster-management
# Expected output: Multiple RHACM pods in Running state

# Get RHACM console URL
oc get route multicloud-console -n open-cluster-management -o jsonpath='{.spec.host}'
```

**⚠️ Troubleshooting:**
```bash
# Check MultiClusterHub status
oc describe multiclusterhub multiclusterhub -n open-cluster-management

# Check operator logs
oc logs -n open-cluster-management -l name=multiclusterhub-operator
```

### 5.5 Install Red Hat OpenShift Service Mesh (Optional)

**📝 Note:** Service Mesh is optional but provides advanced traffic management and observability.

#### Install Required Operators (in order):

**Step 1: Install Elasticsearch Operator**

Via Console:
1. **Operators** → **OperatorHub**
2. Search: **"OpenShift Elasticsearch Operator"**
3. Install with defaults

Via CLI:
```bash
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: elasticsearch-operator
  namespace: openshift-operators
spec:
  channel: stable
  name: elasticsearch-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**Step 2: Install Red Hat OpenShift distributed tracing platform (Jaeger)**

Via Console:
1. **Operators** → **OperatorHub**
2. Search: **"Red Hat OpenShift distributed tracing platform"**
3. Install with defaults

Via CLI:
```bash
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: jaeger-product
  namespace: openshift-operators
spec:
  channel: stable
  name: jaeger-product
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**Step 3: Install Kiali Operator**

Via Console:
1. **Operators** → **OperatorHub**
2. Search: **"Kiali Operator"**
3. Install with defaults

Via CLI:
```bash
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: kiali-ossm
  namespace: openshift-operators
spec:
  channel: stable
  name: kiali-ossm
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**Step 4: Install Red Hat OpenShift Service Mesh**

Via Console:
1. **Operators** → **OperatorHub**
2. Search: **"Red Hat OpenShift Service Mesh"**
3. Install with defaults

Via CLI:
```bash
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: servicemeshoperator
  namespace: openshift-operators
spec:
  channel: stable
  name: servicemeshoperator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

**✅ Verification:**
```bash
# Check all Service Mesh operators
oc get csv -n openshift-operators | grep -E "elasticsearch|jaeger|kiali|servicemesh"
# Expected output: All four operators with "Succeeded" status

# Verify Service Mesh API resources
oc api-resources | grep servicemesh
# Expected output: ServiceMeshControlPlane, ServiceMeshMemberRoll, etc.
```

### 5.6 Summary of Installed Operators

Verify all operators are installed:

```bash
# List all installed operators
oc get csv -n openshift-operators

# Expected operators:
# - openshift-pipelines-operator
# - openshift-gitops-operator
# - cert-manager-operator
# - advanced-cluster-management (if installed)
# - servicemeshoperator (if installed)
# - elasticsearch-operator (if Service Mesh installed)
# - jaeger-product (if Service Mesh installed)
# - kiali-ossm (if Service Mesh installed)
```

**📝 Installation Time Estimates:**
- OpenShift Pipelines: 2-3 minutes
- OpenShift GitOps: 3-5 minutes
- cert-manager: 2-3 minutes
- RHACM: 10-15 minutes
- Service Mesh (all operators): 10-15 minutes

---

## 6. Step 5: Deploy Pipeline Infrastructure

Now we'll deploy the Tekton pipeline components.

### 6.1 Apply Service Account and RBAC

```bash
# Apply pipeline service account
oc apply -f pipelines/resources/pipeline-sa.yaml -n saas-cicd
```

**✅ Verification:**
```bash
oc get serviceaccount pipeline-sa -n saas-cicd
# Expected output:
# NAME          SECRETS   AGE
# pipeline-sa   2         1m
```

### 6.2 Link Secrets to Service Account

```bash
# Link Git credentials
oc secrets link pipeline-sa git-credentials -n saas-cicd

# Link registry credentials
oc secrets link pipeline-sa registry-credentials -n saas-cicd

# Verify secrets are linked
oc describe serviceaccount pipeline-sa -n saas-cicd
# Expected output: Should show git-credentials and registry-credentials in Secrets section
```

### 6.3 Deploy Pipeline Tasks

```bash
# Apply all pipeline tasks
oc apply -f pipelines/tasks/ -n saas-cicd
```

**✅ Verification:**
```bash
oc get tasks -n saas-cicd
# Expected output:
# NAME                  AGE
# git-clone-task        1m
# build-image-task      1m
# run-tests-task        1m
# security-scan-task    1m
# update-gitops-task    1m

# Describe a task to see its details
oc describe task git-clone-task -n saas-cicd
```

### 6.4 Deploy Main Pipeline

```bash
# Apply the main pipeline
oc apply -f pipelines/pipeline.yaml -n saas-cicd
```

**✅ Verification:**
```bash
oc get pipeline -n saas-cicd
# Expected output:
# NAME               AGE
# saas-app-pipeline  1m

# View pipeline details
tkn pipeline describe saas-app-pipeline -n saas-cicd
# Expected output: Pipeline details with all tasks listed
```

### 6.5 Deploy Triggers and Event Listener

```bash
# Apply trigger binding
oc apply -f pipelines/triggers/trigger-binding.yaml -n saas-cicd

# Apply trigger template
oc apply -f pipelines/triggers/trigger-template.yaml -n saas-cicd

# Apply event listener
oc apply -f pipelines/triggers/event-listener.yaml -n saas-cicd
```

**✅ Verification:**
```bash
# Check trigger resources
oc get triggerbinding,triggertemplate,eventlistener -n saas-cicd
# Expected output:
# NAME                                          AGE
# triggerbinding.triggers.tekton.dev/...        1m
# triggertemplate.triggers.tekton.dev/...       1m
# eventlistener.triggers.tekton.dev/...         1m

# Check event listener pod
oc get pods -n saas-cicd -l eventlistener=saas-app-webhook
# Expected output: Event listener pod in Running state

# Get event listener service
oc get svc -n saas-cicd -l eventlistener=saas-app-webhook
# Expected output: Service for event listener
```

### 6.6 Expose Event Listener via Route

```bash
# Create route for webhook
oc expose svc el-saas-app-webhook -n saas-cicd

# Get the webhook URL
export WEBHOOK_URL=$(oc get route el-saas-app-webhook -n saas-cicd -o jsonpath='{.spec.host}')
echo "Webhook URL: https://${WEBHOOK_URL}"

# Save this URL - you'll need it in Step 12
echo "https://${WEBHOOK_URL}" > webhook-url.txt
```

**✅ Verification:**
```bash
# Check route
oc get route el-saas-app-webhook -n saas-cicd
# Expected output: Route with host URL

# Test webhook endpoint (should return 200 or 405)
curl -k https://${WEBHOOK_URL}
# Expected output: Some response (not 404)
```

### 6.7 Grant Pipeline Service Account Permissions

The pipeline needs permissions to update GitOps manifests and interact with ArgoCD:

```bash
# Grant edit permissions in application namespaces
oc adm policy add-role-to-user edit system:serviceaccount:saas-cicd:pipeline-sa -n saas-app-dev
oc adm policy add-role-to-user edit system:serviceaccount:saas-cicd:pipeline-sa -n saas-app-staging
oc adm policy add-role-to-user edit system:serviceaccount:saas-cicd:pipeline-sa -n saas-app-prod

# Grant permissions to interact with ArgoCD
oc adm policy add-role-to-user admin system:serviceaccount:saas-cicd:pipeline-sa -n openshift-gitops
```

**✅ Verification:**
```bash
# Verify role bindings
oc get rolebinding -n saas-app-dev | grep pipeline-sa
oc get rolebinding -n saas-app-staging | grep pipeline-sa
oc get rolebinding -n saas-app-prod | grep pipeline-sa
oc get rolebinding -n openshift-gitops | grep pipeline-sa
```

**📝 Summary:**
At this point, you have:
- ✅ Pipeline service account with proper permissions
- ✅ All pipeline tasks deployed
- ✅ Main pipeline deployed
- ✅ Event listener ready to receive webhooks
- ✅ Webhook URL for Git repository configuration

---

## 7. Step 6: Configure GitOps (ArgoCD)

### 7.1 Verify ArgoCD Installation

```bash
# Check ArgoCD instance
oc get argocd -n openshift-gitops
# Expected output:
# NAME               AGE
# openshift-gitops   10m

# Check ArgoCD pods
oc get pods -n openshift-gitops
# Expected output: All pods in Running state
```

### 7.2 Access ArgoCD UI

```bash
# Get ArgoCD URL
export ARGOCD_URL=$(oc get route openshift-gitops-server -n openshift-gitops -o jsonpath='{.spec.host}')
echo "ArgoCD URL: https://${ARGOCD_URL}"

# Get admin password
export ARGOCD_PASSWORD=$(oc get secret openshift-gitops-cluster -n openshift-gitops -o jsonpath='{.data.admin\.password}' | base64 -d)
echo "Admin Username: admin"
echo "Admin Password: ${ARGOCD_PASSWORD}"

# Save credentials
echo "ArgoCD URL: https://${ARGOCD_URL}" > argocd-credentials.txt
echo "Username: admin" >> argocd-credentials.txt
echo "Password: ${ARGOCD_PASSWORD}" >> argocd-credentials.txt
```

**📝 Login to ArgoCD UI:**
1. Open browser and navigate to the ArgoCD URL
2. Accept the self-signed certificate warning
3. Login with username `admin` and the password from above
4. You should see the ArgoCD dashboard

### 7.3 Login to ArgoCD via CLI

```bash
# Login to ArgoCD
argocd login ${ARGOCD_URL} --username admin --password ${ARGOCD_PASSWORD} --insecure

# Verify login
argocd account get-user-info
# Expected output: User information for admin
```

**✅ Verification:**
```bash
# List ArgoCD clusters
argocd cluster list
# Expected output: At least the local cluster (in-cluster)
```

### 7.4 Configure Git Repository in ArgoCD

```bash
# Add Git repository to ArgoCD
argocd repo add https://github.com/${GITHUB_USER}/mcsp-scenario1.git \
  --username ${GIT_USERNAME} \
  --password ${GIT_TOKEN} \
  --insecure-skip-server-verification

# Verify repository is added
argocd repo list
# Expected output: Your repository listed
```

**Alternative: Via UI:**
1. In ArgoCD UI, click **Settings** (gear icon)
2. Click **Repositories**
3. Click **Connect Repo**
4. Select **VIA HTTPS**
5. Fill in:
   - **Repository URL**: `https://github.com/<YOUR_GITHUB_USERNAME>/mcsp-scenario1.git`
   - **Username**: Your GitHub username
   - **Password**: Your personal access token
6. Click **Connect**
7. Status should show "Successful"

### 7.5 Deploy ArgoCD Applications

```bash
# Deploy all three applications (dev, staging, production)
oc apply -f gitops/applications/saas-app.yaml -n openshift-gitops
```

**✅ Verification:**
```bash
# Check applications
oc get applications -n openshift-gitops
# Expected output:
# NAME                            SYNC STATUS   HEALTH STATUS
# saas-customer-portal-dev        OutOfSync     Missing
# saas-customer-portal-staging    OutOfSync     Missing
# saas-customer-portal-production OutOfSync     Missing

# View application details
argocd app list
# Expected output: Three applications listed

# Get detailed status of dev application
argocd app get saas-customer-portal-dev
```

**📝 Note:** Applications will show "OutOfSync" and "Missing" because we haven't built and pushed the container image yet. This is expected!

### 7.6 Configure ArgoCD Application Sync Policies

The applications are already configured with sync policies in the YAML:
- **Dev**: Auto-sync enabled (automatic deployment)
- **Staging**: Auto-sync enabled (automatic deployment)
- **Production**: Manual sync required (requires approval)

Verify sync policies:

```bash
# Check dev application sync policy
argocd app get saas-customer-portal-dev | grep -A 5 "Sync Policy"
# Expected output: Shows automated sync enabled

# Check production application sync policy
argocd app get saas-customer-portal-production | grep -A 5 "Sync Policy"
# Expected output: Shows manual sync (no automated section)
```

### 7.7 Grant ArgoCD Permissions to Application Namespaces

```bash
# Grant ArgoCD permissions to manage application namespaces
oc adm policy add-role-to-user admin system:serviceaccount:openshift-gitops:openshift-gitops-argocd-application-controller -n saas-app-dev
oc adm policy add-role-to-user admin system:serviceaccount:openshift-gitops:openshift-gitops-argocd-application-controller -n saas-app-staging
oc adm policy add-role-to-user admin system:serviceaccount:openshift-gitops:openshift-gitops-argocd-application-controller -n saas-app-prod
```

**✅ Verification:**
```bash
# Verify role bindings
oc get rolebinding -n saas-app-dev | grep argocd
oc get rolebinding -n saas-app-staging | grep argocd
oc get rolebinding -n saas-app-prod | grep argocd
```

### 7.8 Configure ArgoCD Notifications (Optional)

To receive notifications about deployments:

```bash
# Create notification configuration
cat <<EOF | oc apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: openshift-gitops
data:
  service.slack: |
    token: <YOUR_SLACK_BOT_TOKEN>
  template.app-deployed: |
    message: |
      Application {{.app.metadata.name}} is now running new version.
    slack:
      attachments: |
        [{
          "title": "{{ .app.metadata.name}}",
          "title_link":"{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [
          {
            "title": "Sync Status",
            "value": "{{.app.status.sync.status}}",
            "short": true
          },
          {
            "title": "Repository",
            "value": "{{.app.spec.source.repoURL}}",
            "short": true
          }
          ]
        }]
  trigger.on-deployed: |
    - when: app.status.operationState.phase in ['Succeeded']
      send: [app-deployed]
EOF
```

**📝 Summary:**
At this point, you have:
- ✅ ArgoCD installed and accessible
- ✅ Git repository connected to ArgoCD
- ✅ Three ArgoCD applications created (dev, staging, production)
- ✅ Proper permissions configured
- ✅ Applications ready to sync (waiting for container image)

---

## 8. Step 7: Configure RHACM

**📝 Note:** Skip this section if you're not using RHACM or doing single-cluster deployment.

### 8.1 Verify RHACM Installation

```bash
# Check MultiClusterHub status
oc get multiclusterhub -n open-cluster-management
# Expected output:
# NAME              STATUS    AGE
# multiclusterhub   Running   15m

# Check RHACM console URL

REGISTRY_SERVER} \
  --docker-username=${REGISTRY_USERNAME} \
  --docker-password=${REGISTRY_PASSWORD} \
  --docker-email=${REGISTRY_EMAIL} \
  -n saas-cicd
oc secrets link pipeline-sa registry-credentials -n saas-cicd
```

#### ArgoCD Application Not Syncing

**Symptoms:** ArgoCD shows "OutOfSync" but doesn't sync automatically

**Solutions:**
```bash
# Check ArgoCD application status
argocd app get saas-customer-portal-dev

# Check sync policy
oc get application saas-customer-portal-dev -n openshift-gitops -o yaml | grep -A 10 syncPolicy

# Manually sync
argocd app sync saas-customer-portal-dev

# Check ArgoCD application controller logs
oc logs -n openshift-gitops -l app.kubernetes.io/name=openshift-gitops-application-controller

# Verify repository connection
argocd repo list
argocd repo get https://github.com/${GITHUB_USER}/mcsp-scenario1.git
```

#### Application Pods Not Starting

**Symptoms:** Pods in CrashLoopBackOff or ImagePullBackOff

**Solutions:**
```bash
# Check pod status
oc get pods -n saas-app-dev

# Describe pod for details
oc describe pod <POD_NAME> -n saas-app-dev

# Check pod logs
oc logs <POD_NAME> -n saas-app-dev

# For ImagePullBackOff - verify image exists
oc get deployment saas-customer-portal -n saas-app-dev -o yaml | grep image:

# Check if image pull secret is configured
oc get deployment saas-customer-portal -n saas-app-dev -o yaml | grep imagePullSecrets

# For CrashLoopBackOff - check application logs
oc logs <POD_NAME> -n saas-app-dev --previous
```

#### Certificate Not Issuing

**Symptoms:** Certificate stuck in "Pending" state

**Solutions:**
```bash
# Check certificate status
oc describe certificate saas-customer-portal-tls -n saas-app-prod

# Check certificate request
oc get certificaterequest -n saas-app-prod

# Check cert-manager logs
oc logs -n cert-manager -l app=cert-manager

# Check cluster issuer
oc describe clusterissuer letsencrypt-prod

# Verify DNS is configured correctly
nslookup ${APP_URL}

# Check ACME challenge
oc get challenges -n saas-app-prod
```

#### Service Mesh Issues

**Symptoms:** Traffic not routing through service mesh

**Solutions:**
```bash
# Check if sidecar is injected
oc get pods -n saas-app-prod -o jsonpath='{.items[*].spec.containers[*].name}'
# Expected output: Should include "istio-proxy"

# Verify namespace label
oc get namespace saas-app-prod --show-labels | grep istio-injection

# Check Service Mesh Member Roll
oc get smmr -n istio-system -o yaml

# Restart pods to inject sidecar
oc rollout restart deployment saas-customer-portal -n saas-app-prod

# Check Istio proxy logs
oc logs <POD_NAME> -n saas-app-prod -c istio-proxy
```

### 14.2 How to Check Logs

#### Pipeline Logs
```bash
# List pipeline runs
tkn pipelinerun list -n saas-cicd

# View specific pipeline run logs
tkn pipelinerun logs <PIPELINERUN_NAME> -n saas-cicd -f

# View specific task logs
tkn taskrun logs <TASKRUN_NAME> -n saas-cicd

# View logs from OpenShift console
# Pipelines → Pipeline Runs → Select run → Logs tab
```

#### ArgoCD Logs
```bash
# Application controller logs
oc logs -n openshift-gitops -l app.kubernetes.io/name=openshift-gitops-application-controller

# Server logs
oc logs -n openshift-gitops -l app.kubernetes.io/name=openshift-gitops-server

# Repo server logs
oc logs -n openshift-gitops -l app.kubernetes.io/name=openshift-gitops-repo-server
```

#### Application Logs
```bash
# Current logs
oc logs -n saas-app-dev -l app=saas-customer-portal

# Previous logs (if pod crashed)
oc logs -n saas-app-dev -l app=saas-customer-portal --previous

# Follow logs in real-time
oc logs -n saas-app-dev -l app=saas-customer-portal -f

# Logs from specific container (if multiple containers)
oc logs <POD_NAME> -n saas-app-dev -c <CONTAINER_NAME>
```

#### Operator Logs
```bash
# Pipelines operator
oc logs -n openshift-operators -l name=openshift-pipelines-operator

# GitOps operator
oc logs -n openshift-operators -l control-plane=gitops-operator

# cert-manager operator
oc logs -n cert-manager -l app=cert-manager

# Service Mesh operator
oc logs -n openshift-operators -l name=istio-operator
```

### 14.3 How to Debug Pipeline Failures

```bash
# Get pipeline run details
tkn pipelinerun describe <PIPELINERUN_NAME> -n saas-cicd

# Check which task failed
oc get pipelinerun <PIPELINERUN_NAME> -n saas-cicd -o yaml | grep -A 20 conditions

# View failed task logs
tkn taskrun logs <FAILED_TASKRUN_NAME> -n saas-cicd

# Check workspace PVC
oc get pvc -n saas-cicd

# Check service account permissions
oc describe sa pipeline-sa -n saas-cicd

# Manually run a task for debugging
cat <<EOF | oc create -f -
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: debug-task-
  namespace: saas-cicd
spec:
  taskRef:
    name: git-clone-task
  params:
    - name: url
      value: https://github.com/${GITHUB_USER}/mcsp-scenario1.git
    - name: revision
      value: main
  workspaces:
    - name: output
      emptyDir: {}
    - name: ssh-directory
      secret:
        secretName: git-credentials
  serviceAccountName: pipeline-sa
EOF
```

### 14.4 How to Fix ArgoCD Sync Issues

```bash
# Force refresh application
argocd app get saas-customer-portal-dev --refresh

# Hard refresh (ignore cache)
argocd app get saas-customer-portal-dev --hard-refresh

# Sync with prune (remove resources not in Git)
argocd app sync saas-customer-portal-dev --prune

# Sync specific resource
argocd app sync saas-customer-portal-dev --resource apps:Deployment:saas-customer-portal

# View sync status and diff
argocd app diff saas-customer-portal-dev

# Check application events
oc describe application saas-customer-portal-dev -n openshift-gitops

# Reset application to Git state
argocd app sync saas-customer-portal-dev --force --replace
```

### 14.5 How to Verify Operator Status

```bash
# Check all operators
oc get csv -n openshift-operators

# Check specific operator
oc get csv -n openshift-operators | grep <OPERATOR_NAME>

# Describe operator for details
oc describe csv <CSV_NAME> -n openshift-operators

# Check operator pod
oc get pods -n openshift-operators -l name=<OPERATOR_NAME>

# Check operator logs
oc logs -n openshift-operators -l name=<OPERATOR_NAME>

# Check subscription
oc get subscription -n openshift-operators

# Check install plan
oc get installplan -n openshift-operators
```

### 14.6 Emergency Recovery Procedures

#### Reset Pipeline
```bash
# Delete all pipeline runs
oc delete pipelinerun --all -n saas-cicd

# Recreate pipeline
oc delete pipeline saas-app-pipeline -n saas-cicd
oc apply -f pipelines/pipeline.yaml -n saas-cicd
```

#### Reset ArgoCD Application
```bash
# Delete and recreate application
oc delete application saas-customer-portal-dev -n openshift-gitops
oc apply -f gitops/applications/saas-app.yaml -n openshift-gitops
```

#### Reset Application Deployment
```bash
# Delete deployment
oc delete deployment saas-customer-portal -n saas-app-dev

# Let ArgoCD recreate it
argocd app sync saas-customer-portal-dev
```

#### Complete Namespace Reset
```bash
# Delete namespace (WARNING: This deletes everything)
oc delete namespace saas-app-dev

# Recreate namespace
oc create namespace saas-app-dev

# Resync ArgoCD application
argocd app sync saas-customer-portal-dev
```

---

## 🎉 Congratulations!

You have successfully deployed the MCSP Scenario 1 Multi-Cluster SaaS Platform! 

### What You've Accomplished

✅ **CI/CD Pipeline**: Automated build, test, and deployment pipeline with Tekton  
✅ **GitOps**: Declarative deployment management with ArgoCD  
✅ **Multi-Environment**: Dev, Staging, and Production environments  
✅ **Security**: Automated certificate management and security scanning  
✅ **Automation**: Webhook-triggered deployments on Git push  
✅ **Observability**: Monitoring, logging, and tracing capabilities  

### Next Steps

1. **Customize the Application**: Modify the sample app to fit your needs
2. **Add More Environments**: Create additional overlays for more environments
3. **Implement Monitoring**: Set up Prometheus alerts and Grafana dashboards
4. **Configure Backup**: Implement backup strategies for your data
5. **Scale Up**: Add more managed clusters with RHACM
6. **Enhance Security**: Implement network policies and pod security policies
7. **Add Testing**: Expand test coverage in the pipeline
8. **Documentation**: Document your specific customizations

### Useful Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Tekton Documentation](https://tekton.dev/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [RHACM Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Istio Documentation](https://istio.io/latest/docs/)

### Getting Help

- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review the [Architecture Documentation](ARCHITECTURE.md)
- Open an issue in the repository
- Consult Red Hat support (if you have a subscription)

### Maintenance Tips

- Regularly update operators to latest versions
- Monitor pipeline execution times and optimize as needed
- Review and rotate secrets periodically
- Keep Git repository clean and organized
- Monitor resource usage and scale accordingly
- Regularly backup ArgoCD and pipeline configurations

---

**Made with ❤️ by Bob**

*Last Updated: 2026-03-09*
