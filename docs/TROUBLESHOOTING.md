# Troubleshooting Guide - MCSP Scenario 1

## Common Issues and Solutions

### Pipeline Issues

#### Pipeline Run Fails to Start

**Symptoms:**
- PipelineRun stuck in pending state
- No pods created

**Possible Causes:**
1. Service account missing or incorrect
2. Workspace PVC creation failed
3. Resource quotas exceeded

**Solutions:**
```bash
# Check service account
oc get sa pipeline-sa -n saas-cicd

# Check PVC status
oc get pvc -n saas-cicd

# Check resource quotas
oc describe quota -n saas-cicd

# Check events
oc get events -n saas-cicd --sort-by='.lastTimestamp'
```

#### Git Clone Task Fails

**Symptoms:**
- Git clone task fails with authentication error

**Solutions:**
```bash
# Verify git credentials secret
oc get secret git-credentials -n saas-cicd

# Check secret annotation
oc describe secret git-credentials -n saas-cicd

# Test git access
oc run test-git --image=alpine/git --rm -it -- \
  git clone <your-repo-url>

# Recreate secret if needed
oc delete secret git-credentials -n saas-cicd
oc create secret generic git-credentials \
  --from-literal=username=<username> \
  --from-literal=password=<token> \
  -n saas-cicd
```

#### Image Build Fails

**Symptoms:**
- Buildah task fails with permission errors

**Solutions:**
```bash
# Check SCC permissions
oc get scc pipeline-scc

# Verify service account has SCC
oc adm policy who-can use scc pipeline-scc

# Add SCC to service account
oc adm policy add-scc-to-user pipeline-scc \
  system:serviceaccount:saas-cicd:pipeline-sa
```

#### Image Push Fails

**Symptoms:**
- Cannot push image to registry

**Solutions:**
```bash
# Verify registry credentials
oc get secret registry-credentials -n saas-cicd

# Test registry access
podman login quay.io -u <username> -p <password>

# Check registry secret format
oc get secret registry-credentials -n saas-cicd -o yaml
```

### GitOps Issues

#### ArgoCD Application Out of Sync

**Symptoms:**
- Application shows "OutOfSync" status
- Changes not deploying

**Solutions:**
```bash
# Check application status
oc get application saas-customer-portal-dev -n openshift-gitops

# View sync status
argocd app get saas-customer-portal-dev

# Manual sync
argocd app sync saas-customer-portal-dev

# Hard refresh
argocd app sync saas-customer-portal-dev --force
```

#### ArgoCD Cannot Access Git Repository

**Symptoms:**
- "Unable to clone repository" error

**Solutions:**
```bash
# Check ArgoCD repo credentials
argocd repo list

# Add repository
argocd repo add <repo-url> \
  --username <username> \
  --password <token>

# For SSH
argocd repo add <repo-url> \
  --ssh-private-key-path ~/.ssh/id_rsa
```

### Application Issues

#### Pods Not Starting

**Symptoms:**
- Pods stuck in Pending or CrashLoopBackOff

**Solutions:**
```bash
# Check pod status
oc get pods -n saas-app-prod

# Describe pod for events
oc describe pod <pod-name> -n saas-app-prod

# Check logs
oc logs <pod-name> -n saas-app-prod

# Common fixes:
# 1. Image pull errors - check registry credentials
# 2. Resource limits - adjust requests/limits
# 3. Config errors - check ConfigMap/Secrets
```

#### Application Not Accessible

**Symptoms:**
- Cannot access application via route

**Solutions:**
```bash
# Check route
oc get route -n saas-app-prod

# Test route
curl -I https://<route-url>

# Check service
oc get svc saas-customer-portal -n saas-app-prod

# Check endpoints
oc get endpoints saas-customer-portal -n saas-app-prod

# Test service internally
oc run test --image=curlimages/curl --rm -it -- \
  curl http://saas-customer-portal:8080/health
```

### RHACM Issues

#### Managed Cluster Not Available

**Symptoms:**
- Cluster shows as unavailable in RHACM

**Solutions:**
```bash
# Check managed cluster status
oc get managedclusters

# Check cluster conditions
oc describe managedcluster <cluster-name>

# Check klusterlet pods on managed cluster
oc get pods -n open-cluster-management-agent

# Restart klusterlet
oc delete pod -l app=klusterlet -n open-cluster-management-agent
```

#### Policy Not Compliant

**Symptoms:**
- Policy shows non-compliant status

**Solutions:**
```bash
# Check policy status
oc get policies -n open-cluster-management

# View policy details
oc describe policy <policy-name> -n open-cluster-management

# Check policy on managed cluster
oc get policy <policy-name> -n <cluster-namespace>

# Remediate manually if needed
oc apply -f <resource-file>
```

### Certificate Issues

#### Certificate Not Issued

**Symptoms:**
- Certificate stuck in pending state

**Solutions:**
```bash
# Check certificate status
oc get certificate -n saas-app-prod

# Describe certificate
oc describe certificate saas-customer-portal-tls -n saas-app-prod

# Check cert-manager logs
oc logs -l app=cert-manager -n cert-manager

# Check ACME challenge
oc get challenges -n saas-app-prod

# Manual renewal
kubectl cert-manager renew saas-customer-portal-tls -n saas-app-prod
```

### Service Mesh Issues

#### Sidecar Not Injected

**Symptoms:**
- Pods don't have Istio sidecar

**Solutions:**
```bash
# Check namespace label
oc get namespace saas-app-prod --show-labels

# Add injection label
oc label namespace saas-app-prod istio-injection=enabled

# Check ServiceMeshMemberRoll
oc get smmr -n istio-system

# Restart pods to inject sidecar
oc rollout restart deployment saas-customer-portal -n saas-app-prod
```

#### mTLS Connection Failures

**Symptoms:**
- Services cannot communicate

**Solutions:**
```bash
# Check PeerAuthentication
oc get peerauthentication -n saas-app-prod

# Check DestinationRule
oc get destinationrule -n saas-app-prod

# Verify mTLS mode
istioctl authn tls-check <pod-name> -n saas-app-prod

# Check Istio proxy logs
oc logs <pod-name> -c istio-proxy -n saas-app-prod
```

## Debugging Commands

### General Debugging

```bash
# Get all resources in namespace
oc get all -n saas-app-prod

# Check events
oc get events -n saas-app-prod --sort-by='.lastTimestamp'

# Check resource usage
oc adm top pods -n saas-app-prod
oc adm top nodes

# Check logs
oc logs -f <pod-name> -n saas-app-prod

# Execute commands in pod
oc exec -it <pod-name> -n saas-app-prod -- /bin/bash
```

### Network Debugging

```bash
# Test DNS resolution
oc run test-dns --image=busybox --rm -it -- \
  nslookup saas-customer-portal.saas-app-prod.svc.cluster.local

# Test service connectivity
oc run test-curl --image=curlimages/curl --rm -it -- \
  curl http://saas-customer-portal.saas-app-prod.svc.cluster.local:8080/health

# Check network policies
oc get networkpolicies -n saas-app-prod
```

## Getting Help

### Log Collection

```bash
# Collect must-gather
oc adm must-gather

# Collect RHACM must-gather
oc adm must-gather --image=registry.redhat.io/rhacm2/acm-must-gather-rhel8:v2.8

# Collect service mesh must-gather
oc adm must-gather --image=registry.redhat.io/openshift-service-mesh/istio-must-gather-rhel8:2.4
```

### Support Resources

- Red Hat Support: https://access.redhat.com/support
- OpenShift Documentation: https://docs.openshift.com
- Community Forums: https://discuss.openshift.com
- GitHub Issues: <repository-url>/issues
