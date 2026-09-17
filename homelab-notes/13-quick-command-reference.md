# Quick homelab command reference

This is the shorter command-only document I can open when I already know roughly what is wrong and just need the syntax.

NOTE: The application-specific documents contain the context and explanations behind these commands.

---

## Kubernetes

```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl exec -it <pod> -n <namespace> -- /bin/sh
kubectl get svc,ingress,endpoints -A
kubectl get storageclass,pv
kubectl get pvc -A
```


---
## Helm

```bash
helm lint ./chart
helm dependency update ./chart
helm template release ./chart -n namespace
helm upgrade --install release ./chart -n namespace --create-namespace
helm get values release -n namespace -a
helm get manifest release -n namespace
```


---
## Networking

```bash
ip -br addr
ip route
ip rule
ss -lntup
dig <hostname>
curl -vk https://<hostname>
```


---
## NFS

```bash
showmount -e <ip address>
sudo exportfs -v
findmnt
mount | grep nfs
ls -lna <path>
```


---
## Docker

```bash
docker compose config
docker compose up -d
docker compose logs -f
docker inspect <container>
docker exec -it <container> /bin/sh
```


---
## TLS

```bash
openssl s_client -connect <host>:443 -servername <host> -showcerts </dev/null
openssl x509 -in <certificate.crt> -noout -subject -issuer -dates -fingerprint -sha256
curl --cacert homelab-root-ca.crt https://<host>/
```


---
## PostgreSQL

```bash
psql -h <host> -U <user> -d <database>
pg_dump -Fc -h <host> -U <user> -d <database> -f backup.dump
pg_restore -h <host> -U <user> -d <database> --clean --if-exists backup.dump
```

---
