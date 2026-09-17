# Helm and chart development notes

I use Helm for most application and infrastructure deployments. These notes cover the commands I use regularly and the chart templating mistakes that caused the most confusion.

NOTE: Rendering a chart locally with `helm template` has saved me from applying broken manifests more than once.

---

## Useful commands

```bash
# Repo related
helm repo add <name> <url>
helm repo update
helm search repo <term>
```

```bash
# Using dependencies
helm dependency update ./<chart>
helm dependency build ./<chart>
```

```bash
# Local testing
helm lint ./<chart>
helm template <release> ./<chart> -n <namespace>
helm template <release> ./<chart> -n <namespace> -f values.yaml
```

```bash
# Install or upgrade a chart
helm upgrade --install <release> ./<chart> \
  --namespace <namespace> \
  --create-namespace
```

```bash
# Inspect/review a release
helm list -A
helm status <release> -n <namespace>
helm get values <release> -n <namespace>
helm get manifest <release> -n <namespace>
```

```bash
# Rollback and uninstall
helm history <release> -n <namespace>
helm rollback <release> <revision> -n <namespace>
helm uninstall <release> -n <namespace>
```

---

## Tips and tricks

For an umbrella chart, updating a dependency usually requires:

```bash
helm dependency update
helm upgrade --install ...
```

---

## Troubleshooting

### StorageClasses render as one broken YAML document

I saw output resembling:

```yaml
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
```

Each Kubernetes object must be separated by `---`, or generated from separate template files.

Example:

```yaml
{{- range .Values.storageClasses }}
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: {{ .name }}
...
{{- end }}
```

Always verify with:

```bash
helm template csi-storage ./csi-storage
```

### A values change has no effect

Check the actual release values and manifest:

```bash
helm get values <release> -n <namespace> -a
helm get manifest <release> -n <namespace>
```

Common causes:

- Wrong values nesting
- Dependency alias mismatch
- Stale packaged dependency
- Release installed from a different chart path
- Template uses a different key name
- Resource name changed, creating a second object instead of updating the first

---
