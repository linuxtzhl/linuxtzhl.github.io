# Setting up ingress routing, DNS, and load balancer
After finally getting my cluster up and running, I am now ready to deploy some stuff to it. BUT FIRST - I need to make sure that the applications I want to deploy can be accessed in the first place. This can be done using a **LoadBalancer** service along with a **reverse proxy**.

---

## Step 1: LoadBalancer
See:
- https://metallb.io/
- https://github.com/metallb/metallb/tree/main/charts/metallb

It took me some time to realise that this was even step 1 to begin with. I had already deployed my chosen **reverse proxy** (traefik) and realised that I had no way to connect to it.
So after some research I realised that for a **reverse proxy** to work with the cluster, I needed to first deploy MetalLB.
MetalLB is a common **LoadBalancer** used for bare-metal setups (eg. a homelab).

---

## Traefik
https://github.com/akashrajguru/traefik-metallb
https://edwardbeazer.com/posts/kubernetes-traefik-setup-with-metallb/
https://oneuptime.com/blog/post/2026-02-20-metallb-traefik-ingress/view
https://medium.com/@kalyanishah86/setting-up-metallb-traefik-ingress-and-longhorn-storage-for-on-premises-kubernetes-c7f39750f243

---

## Useful commands
helm upgrade --install metallb metallb/metallb -n metallb

kubectl get l2advertisements -n metallb
kubectl get l2advertisements -n metallb -o yaml
kubectl get ipaddresspools -n metallb -o yaml
kubectl get ipaddresspools -n metallb
kubectl get svc -n traefik
kubectl get ingressroute -A
kubectl get pods -n metallb
kubectl get svc traefik -n traefik -o yaml
kubectl logs -n traefik deploy/traefik

helm get values <release-name> -n <namespace>
helm dependency list

kubectl get svc -A
kubectl get deploy -A
kubectl delete svc <svc-name> -n <namespace>
kubectl delete deploy <deploy-name> -n <namespace>