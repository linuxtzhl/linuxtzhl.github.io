# cert-manager and internal TLS notes

I use cert-manager with an internal certificate authority so my local services can use HTTPS without exposing them publicly. This document explains the certificate chain and the browser trust problems I ran into.

NOTE: Client devices only need the root CA certificate. They should never receive the root CA private key or a service private key.

---

## Useful commands

Check issuers and certificates:

```bash
kubectl get issuer,clusterissuer -A
kubectl get certificate,certificaterequest -A
kubectl get challenge,order -A
kubectl describe certificate <name> -n <namespace>
kubectl logs -n cert-manager deployment/cert-manager
```

Inspect a TLS Secret:

```bash
kubectl get secret <secret> -n <namespace> -o yaml
```

Export the root CA certificate:

```bash
kubectl get secret homelab-root-ca -n cert-manager \
  -o jsonpath='{.data.tls\.crt}' | base64 -d > homelab-root-ca.crt
```

Depending on how the Secret was created, the certificate may be stored under `ca.crt` instead:

```bash
kubectl get secret homelab-root-ca -n cert-manager \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > homelab-root-ca.crt
```

Inspect a remote certificate:

```bash
openssl s_client \
  -connect jellyfin.tzhl.home.lab:443 \
  -servername jellyfin.tzhl.home.lab \
  -showcerts </dev/null
```

Test against a local CA explicitly:

```bash
curl --cacert homelab-root-ca.crt \
  https://jellyfin.tzhl.home.lab/
```


---
## Tips and tricks

My internal CA chain is:

```text
SelfSigned Issuer
        ↓
Root CA Certificate and private key
        ↓
CA ClusterIssuer
        ↓
Wildcard or per-service leaf certificates
```

The self-signed issuer is mainly used to bootstrap the root CA certificate. Normal application certificates should be signed by the CA issuer.

### Root CA Secret versus wildcard TLS Secret

The root CA Secret contains:

- Root CA certificate
- Root CA private key

It is used to issue other certificates and must be tightly protected.

The wildcard TLS Secret contains:

- Wildcard leaf certificate
- Wildcard private key
- Sometimes the CA chain

It is used by Traefik for HTTPS.

Client devices need only the **root CA certificate**. They must never receive either private key.

### Installing the CA on Firefox

The message:

```text
This personal certificate can't be installed because you do not own the
corresponding private key which was created when the certificate was requested.
```

means I tried to import the certificate under the personal/client certificate section.

The root CA belongs under:

```text
Settings
→ Privacy & Security
→ Certificates
→ View Certificates
→ Authorities
→ Import
```

I trust it to identify websites.

### Certificate renewal

Once the root CA is trusted, I do not need to reinstall it whenever a normal wildcard or leaf certificate renews. I only need to redistribute trust if I replace the root CA itself.


---
## Troubleshooting

### Firefox: `SEC_ERROR_UNKNOWN_ISSUER`

Likely causes:

- Root CA not installed
- Root CA imported into the wrong certificate category
- Wrong CA exported
- Browser uses a separate trust store
- Server is not sending the expected certificate
- Hostname resolves to a different server

Check the served issuer:

```bash
openssl s_client \
  -connect jellyfin.tzhl.home.lab:443 \
  -servername jellyfin.tzhl.home.lab \
  -showcerts </dev/null
```

Check the root CA details:

```bash
openssl x509 -in homelab-root-ca.crt -noout -subject -issuer -fingerprint -sha256
```

For a self-signed root CA, subject and issuer should normally match.

### `openssl s_client` says `Verification: OK`, but Firefox fails

OpenSSL may be using a CA file or system store that differs from Firefox's store. Browser trust must be checked separately.

### Certificate hostname mismatch

The wildcard:

```text
*.tzhl.home.lab
```

matches:

```text
jellyfin.tzhl.home.lab
```

but not:

```text
app.media.tzhl.home.lab
```

A wildcard covers one label only.

---
