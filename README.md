# Welcome!
Welcome to my Homelab Repo for my Homelabbing journey.

## History
I initially used Docker with Docker Compose files to set up a basic Homelab, however I quickly learned about the limits to this. It was a good experiment to go through with for a couple of weeks and it helped with my learning but I wanted to do something more complex for learning purposes. That's when I thought of using Kubernetes.

## K8s
Kubernetes (K8s) is an open-source platform for automating the deployment, scaling, and management of containerized applications.

## Kubernetes Homelab
My Homelab is starting as a beginner-friendly Kubernetes cluster with 2 RaspberryPis as nodes (pi5 as master + pi4 as worker). This cluster was built/bootstrapped using **kubeadm**. This was done because I want to learn more about cluster architecture, networking, and DevOps fundamentals from the ground up.

---

# Purpose
I am creating this Homelab to meet these goals:
* Understand how Kubernetes actually works
* Learn cluster bootstrapping with **kubeadm**
* Practice Linux administration
* Experiment safely with networking & containers
* Build foundational DevOps skills
* Document everything clearly for future reference

---

## Why kubeadm?
Instead of using lightweight distributions like **k3s**, **minikube**, **microk8s** etc, I used **kubeadm** because it:
* Exposes the full Kubernetes control plane
* Teaches how etcd, API server, and scheduler interact
* Helps understand certificates and cluster security
* Makes upgrades a hands-on learning experience
* Mirrors how many real-world clusters are built

---

# Lab Architecture

## Cluster Setup
* 1 Control Plane (master) node
* 1 worker node
* **containerd** as the container runtime
* Flannel for networking
* Traefik Ingress Controller
* MetalLB for LoadBalancer support

---

## What I’m Learning
* How kubeadm bootstraps a cluster
* What runs inside the control plane
* How pods communicate
* How services and DNS work
* How ingress routing works
* How persistent volumes function
* How rolling updates behave
* Basic RBAC concepts

---

## Bootstrap Steps
High-level process:
1. Use the Raspberry Pi Imager to install PiOS Lite 64bit to the Pis
2. Turn **swap** off (designated space on a disk (either a dedicated partition or a file) which is used as virtual memory when the system's physical RAM is full)
3. Prepare both pis for Kubernetes Networking (requires certain kernel modules)
4. Install containerd
5. Install kubeadm, kubelet, kubectl
6. Initialize Master node
7. Configure kubectl
8. Untaint the Master node
9. Install CNI plugin
10. Join worker node(s) to cluster

For full documentation, see `/docs`.

---
<!--
## Practice Workloads

This lab includes example deployments such as:
* NGINX demo app
* Simple REST API container
* Redis with persistent storage
* Helm-based deployments
* Rolling update experiments

---

## Networking Concepts Practiced
* Pod networking
* ClusterIP vs NodePort
* Ingress routing
* LoadBalancer via MetalLB
* NetworkPolicies (basic examples)

---

## Observability (Beginner Level)
* Metrics Server
* Basic Prometheus setup
* Simple Grafana dashboards
* kubectl logs & describe workflows

---

## Security (Learning Phase)
* Basic RBAC roles
* Service accounts
* Secret objects
* Pod security standards (baseline)

Focus is understanding — not full hardening (yet).

---

## Documentation Style
Each major concept has:
* Explanation
* Command breakdown
* Troubleshooting notes
* Lessons learned

This repo is both infrastructure **and** study notebook.

---
-->

## Roadmap
* [ ] Add GitOps (ArgoCD)
* [ ] Automate provisioning with Terraform
* [ ] Introduce High Availability control plane
* [ ] Add monitoring stack
* [ ] Practice cluster upgrades
* [ ] Implement stricter security policies

---

## Who This Is For
* Beginners learning Kubernetes
* DevOps students
* Engineers wanting to understand kubeadm
* Anyone who prefers learning by building
