# Flannel and container networking notes

Flannel was one of the first parts of the cluster that made it obvious how many layers Kubernetes networking has. These are the checks I used for CNI binaries, Pod CIDRs, routes, and CoreDNS problems.

CONTEXT: My Pod network uses `10.244.0.0/16`, which must match the value used when the cluster was initialised.

---

## Useful commands

Check Flannel:

```bash
kubectl get pods -n kube-flannel
kubectl logs -n kube-flannel daemonset/kube-flannel-ds
```

Check CNI binaries on every node:

```bash
ls -la /opt/cni/bin
ls -la /usr/lib/cni
```

Check CNI configuration:

```bash
ls -la /etc/cni/net.d
cat /etc/cni/net.d/*
```

Inspect routes:

```bash
ip route
ip link
```

Check Pod CIDR allocation:

```bash
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.podCIDR}{"\n"}{end}'
```


---
## Tips and tricks

My Pod CIDR is:

```text
10.244.0.0/16
```

This must agree with the Flannel configuration and the CIDR supplied during `kubeadm init`.

The CNI plugin binary path depends on the installation. I should not add obsolete kubelet command-line flags without checking my Kubernetes version and packaging.


---
## Troubleshooting

### `failed to find plugin "flannel" in path [/usr/lib/cni]`

This means the node cannot find the required CNI executable.

Check both common locations:

```bash
ls -la /usr/lib/cni
ls -la /opt/cni/bin
```

Install the standard CNI plugin package or place the binaries in the path expected by the runtime. Then restart kubelet:

```bash
sudo systemctl restart containerd
sudo systemctl restart kubelet
```

Recheck:

```bash
kubectl get pods -A -o wide
sudo journalctl -u kubelet -n 200 --no-pager
```

### CoreDNS stuck in `ContainerCreating`

I inspect the Pod events:

```bash
kubectl describe pod -n kube-system <coredns-pod>
```

When CoreDNS is stuck before starting, the problem is often CNI networking rather than CoreDNS configuration.

### `unknown flag: --cni-bin-dir`

The flag is not valid for my current kubelet packaging/version. CNI paths should be configured through the runtime/package configuration rather than blindly adding old kubelet flags.

---
