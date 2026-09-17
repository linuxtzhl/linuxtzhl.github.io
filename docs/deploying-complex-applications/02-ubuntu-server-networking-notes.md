# Ubuntu Server and network notes for my Kubernetes nodes

These are the commands and fixes I used while managing Ubuntu Server on the Raspberry Pi nodes, especially when moving between Wi-Fi and Ethernet and troubleshooting lost DHCP leases.

---

## Useful commands

```bash
# Check network setup
ip addr
ip route
networkctl
networkctl status eth0
networkctl status wlan0
```

```bash
# Check status and errors
sudo systemctl status systemd-networkd
sudo journalctl -u systemd-networkd -b
sudo journalctl -u systemd-networkd -b | grep -i dhcp
```

```bash
# Edit netplan and check changes
sudo nano /etc/netplan/50-cloud-init.yaml
sudo netplan generate
sudo netplan try
sudo netplan apply
ls -la /etc/netplan
ls -la /run/systemd/network
```

```bash
# Restart networking
sudo systemctl restart systemd-networkd
```
---
