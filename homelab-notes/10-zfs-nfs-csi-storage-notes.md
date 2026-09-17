# ZFS, NFS, and Kubernetes CSI storage notes

Storage caused some of the most time-consuming problems in the build. These notes collect the ZFS, NFS, StorageClass, PV/PVC, mount, UID/GID, and hardlink lessons I needed for the media stack.

---

## Useful commands

### ZFS

```bash
zpool status
zpool list
zfs list
zfs get all <dataset>
```

Snapshots:

```bash
sudo zfs snapshot <pool>/<dataset>@manual-$(date +%F)
zfs list -t snapshot
```

### NFS server

Show exports:

```bash
sudo exportfs -v
sudo exportfs -ra
sudo systemctl status nfs-server
```

Check permissions numerically:

```bash
ls -lna /homelab
find /homelab -maxdepth 2 -type d -printf '%u:%g %m %p\n'
```

### NFS client

List exports:

```bash
showmount -e <server IP Address>
```

Manual mount test:

```bash
sudo mkdir -p /mnt/nfs-test
sudo mount -t nfs4 <server IP Address>:/k8s /mnt/nfs-test
mount | grep nfs
touch /mnt/nfs-test/write-test
sudo umount /mnt/nfs-test
```

### Kubernetes storage

```bash
kubectl get storageclass
kubectl get pv
kubectl get pvc -A
kubectl describe pvc <pvc> -n <namespace>
kubectl describe pv <pv>
```

Find mounts in a pod:

```bash
kubectl exec -it <pod> -n <namespace> -- mount
kubectl exec -it <pod> -n <namespace> -- df -h
kubectl exec -it <pod> -n <namespace> -- ls -lna /data
```


---
## Tips and tricks

### StorageClasses

My NFS StorageClass pattern is:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-k8s
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: nfs.csi.k8s.io
parameters:
  server: "<server IP Address>"
  share: "/k8s"
reclaimPolicy: Retain
volumeBindingMode: Immediate
allowVolumeExpansion: true
```

Other classes can point at:

```text
/homelab/downloads
/homelab/media/tv
/homelab/media/movies
```

I only mark one StorageClass as default.

### `storageClassName` versus `storageClass`

The Kubernetes PVC field is:

```yaml
spec:
  storageClassName: nfs-k8s
```

`storageClass` is sometimes used as a Helm values key, but it is not the native PVC field.

### Sharing a PV

A PV normally binds to one PVC.

Multiple Pods may mount the same `ReadWriteMany` PVC, but creating several unrelated PVCs does not make them all bind to the same already-bound PV.

For media applications, I can:

- Share one RWX PVC between several Pods, or
- Use separate dynamically provisioned PVCs backed by carefully chosen NFS shares

For hardlinks, source and destination must be on the same filesystem/mount.

### Reclaim policy

With:

```yaml
reclaimPolicy: Retain
```

deleting a PVC does not delete the underlying NFS data. The PV may enter `Released` and require manual cleanup or claimRef removal before reuse.


---
## Troubleshooting

### `mount failed: exit status 32`

I inspect the full Pod event:

```bash
kubectl describe pod <pod> -n <namespace>
```

Then test the same export from the affected node:

```bash
sudo mount -v -t nfs4 <server IP Address>:/k8s /mnt/nfs-test
```

Common causes:

- Incorrect exported path
- NFS server not reachable
- Client subnet missing from `/etc/exports`
- Firewall
- Missing NFS client utilities
- NFSv3 versus NFSv4 path mismatch
- Permission or root-squash behaviour

### `permission denied`

Numeric IDs matter more than usernames.

Check inside the pod and on the NAS:

```bash
id
ls -lna /data
touch /data/test-file
```

If containers use `PUID=1000` and `PGID=1000`, the NFS directories should be writable by those numeric IDs or by an appropriate shared group.

I avoid solving permissions with `chmod -R 777` unless it is a very temporary diagnostic step.


### File begins with zero bytes in a container

I used:

```bash
od -An -tx1 -N32 "<file>"
```

and saw zeros. This is not enough by itself to prove NFS corruption. It can indicate:

- A sparse or preallocated incomplete file
- A download that has not written the first piece
- The wrong file/path
- A stale or unexpected backing file

I compare:

```bash
stat "<file>"
du -h "<file>"
du --apparent-size -h "<file>"
file "<file>"
```
