# Kubernetes and kubeadm notes from building my cluster

This document contains the day-to-day commands and some of the less obvious problems I ran into after provisioning my bare-metal Kubernetes cluster with kubeadm.

NOTE: These notes continue from my existing Ubuntu Server cluster setup notes and focus more on operating and repairing the cluster.

---

## Useful commands

```bash
# Rollout methods
kubectl rollout status deployment/<name> -n <namespace>
kubectl rollout restart deployment/<name> -n <namespace>
kubectl rollout history deployment/<name> -n <namespace>
kubectl rollout undo deployment/<name> -n <namespace>
```

---
