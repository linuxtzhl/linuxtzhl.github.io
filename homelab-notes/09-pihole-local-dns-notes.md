# Pi-hole and local DNS notes

Pi-hole handles the local DNS records for my homelab. These notes cover how I point service names at Traefik and how I checked clients that were bypassing Pi-hole or returning unexpected public addresses.

CONTEXT: My internal DNS suffix is `tzhl.home.lab`.

---

## Useful commands

Check DNS from a client:

```bash
nslookup jellyfin.tzhl.home.lab
dig jellyfin.tzhl.home.lab
dig @<PIHOLE_IP> jellyfin.tzhl.home.lab
```

Check Pi-hole pods and service:

```bash
kubectl get pods,svc -n pihole -o wide
kubectl logs -n pihole deployment/pihole
```

Check port 53:

```bash
sudo ss -lntup | grep ':53'
```

Flush caches where appropriate:

```bash
sudo resolvectl flush-caches
```


---
## Tips and tricks

I use Pi-hole local DNS records so names such as:

```text
pihole.tzhl.home.lab
jellyfin.tzhl.home.lab
traefik.tzhl.home.lab
```

resolve to the Traefik LoadBalancer address.

The DNS record generally points to Traefik, not directly to the application Pod or ClusterIP.

Pi-hole itself can use HTTPS by being proxied through Traefik. Pi-hole does not need to terminate TLS directly for the web UI.


---
## Troubleshooting

### `dig` returns both a public IP and a local IP

Possible causes:

- A public DNS record still exists
- The client is querying more than one DNS server
- Search domains or conditional forwarding are involved
- Browser secure DNS/DoH bypasses Pi-hole
- Cached response

I check exactly which DNS server answered:

```bash
dig jellyfin.tzhl.home.lab
resolvectl status
```

I disable browser DoH for the internal namespace or configure it not to bypass local DNS.

### Pi-hole DNS works on one client but not another

Check the DHCP-provided DNS server on each client. Also check whether a VPN, corporate agent, or browser DoH overrides system DNS.

### Pi-hole web page is reachable by IP but not name

This is usually a local DNS record or client DNS configuration issue, not a Kubernetes Service issue.

---
