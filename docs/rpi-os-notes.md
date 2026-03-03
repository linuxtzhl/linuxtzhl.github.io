# What I used to set up a new Kubernetes cluster using **kubeadm**
When researching, I found quite a few guides on how to provision a K8s cluster on RaspberryPis. These are the few I used and edited to get things up and running:
* `https://amrith.me/posts/tech/k8s/install-k8s-raspberrypi/`
* `https://medium.com/@bsatnam98/setup-of-a-kubernetes-cluster-v1-29-on-raspberry-pis-a95b705c04c1`
* `https://medium.com/@olorunfemikawonise_56441/simplifying-kubernetes-installation-on-ubuntu-using-a-bash-shell-script-d75fed68a31`

NOTE: None of these three resources worked when simply following the steps, so I had to do more troubleshooting and research which will be documented below.

---

# THESE NOTES ARE A LEARNING EXPERIENCE AND DID NOT WORK
See /docs/ubuntu-server-notes.md

---

## My full bare-metal setup
Listed below is a full list of hardware used for the Kubernetes cluster:
- RaspberryPi 5 (Master node)
    - 64-bit Arm Cortex-A76 CPU (4 Cores)
    - 128GB Storage
    - 8GB RAM
    - RaspberryPi OS Lite (64bit)

- RaspberryPi 5 (Worker node)
    - 64-bit Arm Cortex-A76 CPU (4 Cores)
    - 64GB Storage
    - 4GB RAM
    - RaspberryPi OS Lite (64bit)

---

## Preparing the Pis for Kubernetes

---

### Ensure static IPs
There are many ways to do this, however, as my router allows for IP reservations - I used that option. This allowed me to reserve the IP addresses of the rpi's based on their respective MAC addresses.

NOTE: There are many other ways to do this within the terminal see `https://www.freecodecamp.org/news/setting-a-static-ip-in-ubuntu-linux-ip-address-tutorial/`

---

### Turn **swap** off
NOTE: Most of this process should be done on **ALL NODES** as **root** so either login as **root** with `sudo su root` or put `sudo` at the start of each command.

This step caused me a lot of trouble as I tried turning **swap** off in many ways - none of which worked. I later realised that this was because the OS I am using stores the **swap** config in a different location and must be turned off in a different way. Newer RaspberryPi OS versions use **zram** instead of **dphys-swapfile** or **rpi-swap**.
See `https://forums.raspberrypi.com/viewtopic.php?t=393833`
To disable the **zram**, the following drop-in config was created:

```bash
mkdir /etc/rpi/swap.conf.d/
echo -e "[Main]\nMechanism=none" | tee /etc/rpi/swap.conf.d/90-disable-swap.conf
```
The above can also be done as:
```bash
mkdir /etc/rpi/swap.conf.d/
nano /etc/rpi/swap.conf.d/90-disable-swap.conf
```
Then add the following to the file:
```bash
[Main]
Mechanism=none
```
After a reboot, **swap** should be turned off. This can be checked using `free -m` which will output something like:
```bash
               total        used        free      shared  buff/cache   available
Mem:            8062         923        5515         162        1873        7139
Swap:              0           0           0
```

### Prepare Kernal for Kubernetes Networking
To allow Kubernetes networking, there are certain Kernal modules that are required. 
`overlay` is used for container storage and `br_netfilter` is used for network bridge filtering. 
`net.bridge.bridge-nf-call-iptables = 1` enables the br_netfilter kernel module to pass bridged IPv4 packets to the iptables firewall for processing.
`net.ipv4.ip_forward = 1` enables IP packet forwarding on the host. This allows the system to route packets between different network interfaces.
`net.bridge.bridge-nf-call-ip6tables = 1` performs the same function as bridge-nf-call-iptables, but for IPv6 traffic.

```bash
# Step 1: Load kernel modules
cat <<EOF | tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

# Step 2: Configure kernel parameters
cat <<EOF | tee /etc/sysctl.d/99-kubernetes-k8s.conf
net.bridge.bridge-nf-call-iptables = 1 
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# Step 3: Apply kernel parameter changes
sysctl --system
```

---

## Install **containerd**
**containerd** is an industry-standard, open-source container runtime that manages the complete lifecycle of containers on a host system.
Install **containerd** by running the following:
```bash
apt update
apt install -y containerd
```
Then generate the config file:
`containerd config default > /etc/containerd/config.toml`
Next, the config file needed to be edited to enable the use of **SystemdCgroup** for **cgroup** management:
`nano -l /etc/containerd/config.toml`
Then find the line `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]` (this was at line 128 for me).
Within this section find `SystemdCgroup` and set it to `true`.

Finally, enable and restart **containerd**
```bash
systemctl enable containerd
systemctl restart containerd
```
Surprisingly I had little to no issues with this part. But the hard part was yet to come.

---

## Installing Kubernetes
CONTEXT: I was figuring out all of these steps in Feb 2026 and it took me a few weeks of research to become comfortable enough to go through with it. The installation of **Kubernetes** did not go smoothly for reasons I will describe as I go through the steps.

### Get and update packages
Run `apt-get update` to refresh the package index.
Install dependencies with:
`apt-get install -y apt-transport-https ca-certificates curl gpg`
Then download the public **Kubernetes** GPG public key and save it to the `kubernetes-apt-keyring.gpg` file.
NOTE: `--dearmor` converts the **ASCII-armored key** into **binary** format. This is required by modern **APT** **keyring** handling.

`curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg`

Then create a repository definition using the downloaded key and write the definiton to the `kubernetes.list` file.
`echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list`

### Install kubelet kubeadm kubectl
```bash
apt-get update
apt-get install -y kubelet kubeadm kubectl
```

NOTE: This is where I ran into some issues. When running the `apt-get update` command, I got the following error:
```bash
Warning: GPG error: https://prod-cdn.packages.k8s.io/repositories/isv:/kubernetes:/core:/stable:/v1.32/deb  InRelease: Sub-process /usr/bin/sqv returned an error code (1), error message is: Error: Policy rejected packet type  Caused by:     Signature Packet v3 is not considered secure since 2021-02-01T00:00:00Z
Error: The repository 'https://pkgs.k8s.io/core:/stable:/v1.32/deb  InRelease' is not signed.
Notice: Updating from such a repository can't be done securely, and is therefore disabled by default.
```
I initially thought that this error was saying that *I* did not use the correct gpg signing version when getting the packages, however, after some research I learned that it is actually and issue with the repositories provider (OpenBuildService). There was a temporary fix that I found. See `https://github.com/kubernetes/kubernetes/issues/133532#:~:text=/usr/share/apt/default%2Dsequoia.config%20to%20new%20file%20(in%20new%20parent%20directories)%20/etc/crypto%2Dpolicies/back%2Dends/apt%2Dsequoia.config`
I plan to update this to a more long-term fix later, but for now doing the following fixed the issue (by extending the deprication date from 2026 to 2027):
```bash
mkdir /etc/crypto-policies/back-ends/
cp /usr/share/apt/default-sequoia.config /etc/crypto-policies/back-ends/apt-sequoia.config
nano /etc/crypto-policies/back-ends/apt-sequoia.config
```

---

## Create the Kubernetes cluster
The following process initialises and provisions the Kubernetes cluster and should be done **ONLY ON THE MASTER NODE (control plane)**.
NOTE: I also ran into an issue here. I got an error stating that `node name <hostname> does not exist` where `<hostname>` is the **Hostname** I set for my rpi. I assumed that I got this error because I have a non-default **Hostname** set on my Master node. I edited the default command to look like this:
`kubeadm init --pod-network-cidr=10.244.0.0/16 --service-cidr=10.96.0.0/12 --node-name=<hostname>`
The `--pod-network-cidr=10.244.0.0/16` and `--service-cidr=10.96.0.0/12` are simply the default **CIDR** ranges for **flannel** which is the CNI (Container Network Interface) that I decided to use.
While troubleshooting the above, I noticed some other errors which said:
```bash
[ERROR SystemVerification]: missing required cgroups: memory
[ERROR FileExisting-conntrack]: conntrack not found in system path
```
To fix the first error, I added `cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1` to `/boot/firmware/cmdline.txt`:
`nano /boot/firmware/cmdline.txt`
To fix the second error, I simply downloaded and installed **conntrack**:
`sudo apt-get update && sudo apt-get install -y conntrack`
After doing all of the above, I was finally ready to initialise **Kubernetes** using **kubeadm**
`kubeadm init --pod-network-cidr=10.244.0.0/16 --service-cidr=10.96.0.0/12 --node-name=<hostname>`

---

## Accessing the cluster
After initialisation, I got the following output:
```bash
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a Pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  /docs/concepts/cluster-administration/addons/

You can now join any number of machines by running the following on each node
as root:

  kubeadm join <control-plane-host>:<control-plane-port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```
Where `<control-plane-host>` is your Master node IP address, `<control-plane-port>` is `6443` by default, `<token>` and `<hash>` will be personalised strings. Make a note of the command somewhere safe and **DO NOT SHARE THESE** as anyone with that command on your network can connect to your cluster.
Running `kubectl get pods` I could see that my Master node had `STATUS - NotReady`. 

I originally thought that this was due to the node needing to be **untainted** by running `kubectl taint nodes --all node-role.kubernetes.io/control-plane-` as that is what the guide suggests.
NOTE: The above command removes (the dash at the end means remove) the **taint** called `node-role.kubernetes.io/control-plane` from `--all` nodes (at this moment there is only one node so this will only affect the Master node)

However, I learned that this command for **untainting** the Master node is only for single node setups. As my cluster is using two nodes I did not need to **untaint** anything. 
I did some troubleshooting and ran the following commands to reset `kubeadm` and `kubelet` which fixed the issue:
```bash
kubeadm reset
systemctl restart kubelet
```

---

## Installing flannel
**SO**... Here is where I realised (after some hours of troubleshooting) that my setup was entirely inappropriate as I have been using RaspberryPi OS Lite 64bit... Which apparently is not suitable for **Kubernetes** clusters as the `cgroup` parameter is set to `disabled` in the firmware. This cannot be changed. So at this point I wiped the OS for both pis and setup Ubuntu Server. Hopefully it works better.
