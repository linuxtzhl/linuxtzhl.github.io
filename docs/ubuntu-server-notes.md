# A new set of notes using the correct OS on two Raspberry Pi 5's
NOTE: See [/docs/rpi-os-notes.md](./rpi-os-notes.md) for previous setup attempt (DID NOT WORK)

---

## My full bare-metal setup
Listed below is a full list of hardware used for the Kubernetes cluster:
- RaspberryPi 5 (Master node)
    - 64-bit Arm Cortex-A76 CPU (4 Cores)
    - 128GB Storage
    - 8GB RAM
    - Ubuntu Server OS 25.10 (64bit)

- RaspberryPi 5 (Worker node)
    - 64-bit Arm Cortex-A76 CPU (4 Cores)
    - 64GB Storage
    - 4GB RAM
    - Ubuntu Server OS 25.10 (64bit)

---

## Full reset
SO... Because I messed up on my first attempt, I decided to automate the process for provisioning a 2 (or more) node **Kubernetes Cluster** with **ansible**. 
NOTE: I used this `https://medium.com/karlmax-berlin/how-to-install-kubernetes-on-raspberry-pi-53b4ce300b58` code as a template for my script.
See /code/examples/example-ansible.yml
The script mostly speaks for itself but I will journal my process here.

---

## Using ansible
Here are some docs that got me through this process `https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/index.html`
At work I have used **ansible** a bit but I never really understood how useful/powerful it can be when automating any kind of setup.

---

### Step 1: Initial creation of the ansible script
I had found the example **ansible** code when I was first trying to setup a cluster and saved it just in case it came in use. Now that it was time to use it - I copied over the code and started making edits for it to work in my environment.

### Step 2: Tailoring
With my new **ansible** script ready to be edited, I started by checking the code to see which parts of it were not needed or simply redundant and removing anything that wasn't needed. 
For example: Lines 9-54 are not needed for me because the OS I am now using has **swap** off by default and I manually run `sudo apt update -y && sudo apt upgrade -y` everytime I first SSH into a newly installed OS.
This step also included making sure that any **packages** that needed to be downloaded were the latest version.

### Step 3: Making it work
After removing/commenting out all the extra bits that I didn't need, the next step was to make the script actually work.
For example: Lines 57-63 in my code equates to the following from the linked example:
```yaml
- name: Enable cgroup in /boot/cmdline.txt
    ansible.builtin.lineinfile:
    path: /boot/cmdline.txt
    backrefs: yes
    regexp: '^console(.*) rootwait$'
    line: '\g<0> cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1'
```
I found that the `ansible.builtin.lineinfile` command, with the `regexp` filter just didn't work, so I did the same thing but with old reliable **bash**.
I used my guide from [/docs/rpi-os-notes.md](./rpi-os-notes.md) as a step-by-step process, essentially recreating that manual process as it mostly worked.
This time around I ran into less errors while creating the script. Most of the errors were from incorrect use of **ansible** as I was still getting the hang of the **syntax** and how many times to indent lines.

### Step 4: kubeadm init (going above and beyond)
The **ansible** script that I used as a template stopped after installing a CNI to both nodes, however, I wanted to automate the process as much as I could. So I wrote a few extra lines at the end (before CNI installation) to run `kubeadm init` on the Master node. This code runs the same `kubeadm init` command from my /docs/pi-os-notes.md and uses a **python** script to loop through the two sections of the `kubeadm join` command (outputted from `kubeadm init`) to create the whole command with no line breaks or special characters.

### Step 5: Output checks
After making the appropriate changes and edits, I ran the ansible script with the `--dry-run` tag. This was to ensure the cluster was not actually provisioned and to double check the `kubeadm join` command was configured correctly (if it was not then I wouldn't be able to find the original command which forces a clean-up process and another `kubeadm init`).
Luckily, this worked! So I ran the script without the tag and provisioned my ~~second~~ FIRST cluster!

### Step 6: Join worker node to cluster
Using the `kubeadm join` command, I joined my worker node to the cluster.

### Step 7: Apply CNI (Flannel)
Finally, I used `kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml` to apply a CNI to my cluster from my Master node.

---

## Useful commands
Below are a list of useful commands that can help for troubleshooting and checking:
```bash
#simple checks
kubectl get pods -n kube-system
kubectl get pods -A

systemctl status kubelet
systemctl restart kubelet
journalctl -u kubelet -r
sudo systemctl is-active containerd

#cleanup (only for clean wipe after a kubeadm init)
kubeadm reset
sudorm -rf ~/.kube
sudo rm -rf /var/lib/kubelet/
sudo rm -rf /var/lib/etcd/
sudo rm -rf /etc/kubernetes/
```