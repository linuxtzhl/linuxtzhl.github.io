# How I troubleshoot problems in my homelab

These are the checks and commands that came in handy when something didn't work.

---

## Useful commands

### Cluster health

NOTE: Most of the time, I was using K9s for troubleshooting and generally naviating my cluster, but below are the useful `kubectl` commands that can be used instead

```bash
# All
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get svc -A
kubectl get ingress -A
kubectl get pvc -A
```

```bash
# Deployment with multiple containers
kubectl logs deployment/<deployment> -n <namespace> -c <container>
kubectl exec -it deployment/<deployment> -n <namespace> -c <container> -- /bin/sh
```

```bash
# Networking
ip addr
ip route
ip rule
ss -lntup
ping <ip>
curl -vk https://<host>
nslookup <host>
dig <host>
```

```bash
# Storage
df -h
df -T
mount
findmnt
ls -ln <path>
stat <path>
```
