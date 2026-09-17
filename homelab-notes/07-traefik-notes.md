# Traefik ingress and reverse proxy notes

Traefik is the main entry point for the services in my homelab. I use it for local hostnames, HTTPS, IP allowlists, and even for Docker applications that run outside the Kubernetes cluster.

CONTEXT: Pi-hole resolves my internal `*.tzhl.home.lab` names to the Traefik LoadBalancer address.

---

## Useful commands

Check Traefik:

```bash
kubectl get pods -n traefik
kubectl get svc -n traefik
kubectl logs -n traefik deployment/traefik
kubectl get ingressclass
```

Check routes:

```bash
kubectl get ingress -A
kubectl describe ingress <name> -n <namespace>
kubectl get ingressroute,middleware,tlsoption -A
```

Test a route while bypassing DNS:

```bash
curl -vk --resolve jellyfin.tzhl.home.lab:443:<TRAEFIK_IP> \
  https://jellyfin.tzhl.home.lab/
```

---
## Tips and tricks

### Standard Ingress pattern

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jellyfin
  namespace: media-stack
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - jellyfin.tzhl.home.lab
      secretName: wildcard-tls
  rules:
    - host: jellyfin.tzhl.home.lab
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: jellyfin
                port:
                  number: 80
```

I keep:

```yaml
spec:
  ingressClassName: traefik
```

unless Traefik is configured as the default IngressClass. Being explicit avoids another controller claiming the route.

### Using a wildcard TLS secret

When cert-manager has already issued a wildcard certificate for:

```text
*.tzhl.home.lab
tzhl.home.lab
```

each Ingress can reference the same copied or centrally available TLS secret, subject to namespace rules.

Normal Kubernetes Ingress can only reference a TLS Secret in the same namespace. I therefore either:

- Let cert-manager create a certificate in each application namespace, or
- Replicate the wildcard Secret into those namespaces using a controlled process

I do not put the root CA private key in application namespaces.

---
