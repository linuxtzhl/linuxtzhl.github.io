# MetalLB notes for my bare-metal cluster

MetalLB provides the LoadBalancer addresses that make services such as Traefik reachable on my LAN. These are the resources, commands, and fixes I used while setting it up.

NOTE: The MetalLB pool must not overlap with addresses that my router can hand out through normal DHCP.

---

## Useful commands

Check MetalLB:

```bash
kubectl get pods -n metallb-system
kubectl get ipaddresspools -n metallb-system
kubectl get l2advertisements -n metallb-system
kubectl describe ipaddresspool -n metallb-system <pool>
```

Check LoadBalancer services:

```bash
kubectl get svc -A --field-selector spec.type=LoadBalancer
kubectl describe svc <service> -n <namespace>
```


---
## Tips and tricks

MetalLB needs both:

- An `IPAddressPool`
- An `L2Advertisement`

Example:

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: lan-pool
  namespace: metallb-system
spec:
  addresses:
    - 10.32.1.200-10.32.1.220
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: lan-advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
    - lan-pool
```

I only use an address range that is outside my router's normal DHCP allocation.


---
## Troubleshooting

### LoadBalancer remains `pending`

Check:

```bash
kubectl get ipaddresspools,l2advertisements -n metallb-system
kubectl logs -n metallb-system daemonset/speaker
kubectl logs -n metallb-system deployment/controller
kubectl describe svc <service> -n <namespace>
```

### Shared IP for DNS TCP and UDP services

Pi-hole may need multiple ports on one LoadBalancer IP. A single Service can expose TCP and UDP ports. If multiple Services intentionally share one IP, the MetalLB shared-IP annotation and compatible selectors/traffic policy may be needed.

---
