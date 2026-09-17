# My current homelab environment

This is a snapshot of the homelab as it currently stands. I am keeping the addresses, storage paths, and main design choices here so I do not have to search through several application notes whenever I need some context.

NOTE: This is a working environment rather than a final design. I expect parts of it to change as I add Proxmox nodes and move services around.

---

## Current architecture

I am building a bare-metal Kubernetes cluster on Raspberry Pi hardware running Ubuntu Server.

My main services include:

- Kubernetes installed with `kubeadm`
- Flannel CNI
- MetalLB
- Traefik
- cert-manager
- Pi-hole
- NFS CSI driver
- Jellyfin
- Homarr
- PostgreSQL

---
## My basic design principles

- Keep application configuration on persistent volumes.
- Keep media on NFS-backed shared storage.
- Use `Retain` for important storage.
- Keep Helm charts and Kubernetes manifests in Git.
- Put credentials in Kubernetes Secrets rather than committed values files.
- Use Traefik as the common HTTPS entry point.
- Use Pi-hole for local DNS.
- Trust my internal root CA on client devices rather than bypassing TLS warnings.

---
