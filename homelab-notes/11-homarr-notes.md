# Homarr deployment notes

These notes cover the Homarr encryption secret, Helm environment variables, PostgreSQL connectivity, and the startup error I saw when the required key was missing.

NOTE: The encryption key must remain stable after deployment or previously encrypted data may become unreadable.

---

## Useful commands

Generate a 64-character hexadecimal secret:

```bash
openssl rand -hex 32
```

Create a Kubernetes Secret:

```bash
kubectl create secret generic homarr-secret \
  -n homarr \
  --from-literal=SECRET_ENCRYPTION_KEY='<64-character-hex-value>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Check Homarr:

```bash
kubectl get pods,svc,ingress -n homarr
kubectl logs -n homarr deployment/homarr
```


---
## Tips and tricks

I saw:

```text
SECRET_ENCRYPTION_KEY is required, please generate a 64 character secret in hex format
```

`openssl rand -hex 32` produces 32 random bytes represented by 64 hexadecimal characters.

I store this in a Secret rather than plain `values.yaml`.

My chart/repository structure separates:

```text
dependencies/
applications/homarr/
secrets/
```

Homarr connects to PostgreSQL using the cluster DNS name:

```text
postgresql.postgresql.svc.cluster.local
```

Current database details:

```text
Database: postgres
Username: tzhl
```

The password remains in a Secret.


---
## Troubleshooting

### Invalid environment variable

Check the exact environment variable name expected by the Homarr image/chart version and inspect the rendered Deployment:

```bash
helm template homarr ./applications/homarr
kubectl get deployment homarr -n homarr -o yaml
```

Check whether `envFrom`, `secretKeyRef`, and Secret key names match exactly.

### Encryption key changes after deployment

Changing the encryption key can make existing encrypted data unreadable. I back up and preserve the original value.

### Homarr cannot connect to PostgreSQL

Test DNS and port connectivity from the Homarr pod:

```bash
kubectl exec -it -n homarr deployment/homarr -- \
  getent hosts postgresql.postgresql.svc.cluster.local
```

Use a temporary PostgreSQL client pod for an actual database login test.

---
