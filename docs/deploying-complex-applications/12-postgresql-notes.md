# PostgreSQL deployment and maintenance notes

I decided to start with a standalone PostgreSQL deployment because it is simpler to understand and restore. These notes cover the Kubernetes Services, useful SQL commands, backups, password problems, and future migration.

CONTEXT: The current database is called `postgres` and the application username is `tzhl`; the password remains in a Kubernetes Secret.

---

## Useful commands

Current services in namespace `postgresql`:

```text
postgresql           ClusterIP   10.105.12.234   5432/TCP
postgresql-hl        ClusterIP   None            5432/TCP
postgresql-metrics   ClusterIP                   9187/TCP
```

Inspect:

```bash
kubectl get pods,svc,pvc -n postgresql
kubectl describe statefulset postgresql -n postgresql
kubectl logs -n postgresql statefulset/postgresql
```

Connect from the database pod:

```bash
kubectl exec -it -n postgresql postgresql-0 -- \
  psql -U tzhl -d postgres
```

Run a temporary client:

```bash
kubectl run postgres-client \
  --rm -it \
  --restart=Never \
  --image=postgres:17 \
  --env="PGPASSWORD=<password>" \
  -- psql \
  -h postgresql.postgresql.svc.cluster.local \
  -U tzhl \
  -d postgres
```

Useful `psql` commands:

```sql
\conninfo
\l
\c postgres
\du
\dt
\dn
\d <table>
\x
\timing
\q
```

Create a database and user:

```sql
CREATE USER appuser WITH PASSWORD '<password>';
CREATE DATABASE appdb OWNER appuser;
GRANT ALL PRIVILEGES ON DATABASE appdb TO appuser;
```

Backup:

```bash
PGPASSWORD='<password>' pg_dump \
  -h postgresql.postgresql.svc.cluster.local \
  -U tzhl \
  -d postgres \
  -Fc \
  -f postgres-$(date +%F).dump
```

Restore:

```bash
PGPASSWORD='<password>' pg_restore \
  -h postgresql.postgresql.svc.cluster.local \
  -U tzhl \
  -d postgres \
  --clean \
  --if-exists \
  postgres-YYYY-MM-DD.dump
```


---
## Tips and tricks

### Service meanings

`postgresql`:

- Normal ClusterIP Service
- Applications should normally use this name

`postgresql-hl`:

- Headless Service
- Used for StatefulSet member discovery and direct Pod DNS
- Normal even for a standalone chart

`postgresql-metrics`:

- Exposes PostgreSQL exporter metrics, usually on port `9187`
- Used by Prometheus or another monitoring system

### Standalone PostgreSQL

A standalone instance is appropriate for my current homelab because it is:

- Simpler to understand
- Easier to back up
- Less resource-intensive
- Easier to troubleshoot

The trade-off is downtime if the Pod, node, or storage fails.

The most important protections are:

- Persistent storage
- Tested logical backups
- ZFS/NFS snapshots
- Stable credentials
- Documented restore procedure
- Resource requests
- Monitoring storage capacity


---
## Troubleshooting

### Connection refused

Check:

```bash
kubectl get pods,svc,endpoints -n postgresql
kubectl logs -n postgresql postgresql-0
```

Confirm the application uses port `5432` and the Service DNS name.

### Password authentication failed

Check that the application Secret and PostgreSQL Secret contain the same password. Be careful when changing Helm values after the database has already initialized; some charts do not automatically replace an existing database password merely because a values file changed.

### Database data disappears after reinstall

Check the PVC and reclaim policy before uninstalling:

```bash
kubectl get pvc -n postgresql
kubectl get pv
```

Never assume a Helm uninstall preserves storage without verifying the chart and PVC ownership.

### Future migration

Before moving PostgreSQL:

1. Take `pg_dump` or `pg_dumpall`
2. Verify the backup file
3. Provision the new database
4. Restore
5. Test application connectivity
6. Cut over DNS/Secret configuration
7. Keep the old instance offline but intact until validation is complete

---
