# Hetzner Dedicated Server — CYTools Compute Node

> Quick-reference for reconnecting, managing scans, and rebuilding if needed.
> Activated 2026-02-23. Connection details in local `~/.ssh/config` (not in repo).

---

## Connection

```bash
# Connect via SSH config alias (see setup below)
ssh hetzner
```

SSH authenticates via your ED25519 key. No password.

Add to your local `~/.ssh/config` (NOT in this repo):
```
Host hetzner
    HostName <SERVER_IP>
    User seth
    IdentityFile ~/.ssh/id_ed25519
```

---

## Hardware

| Component | Spec |
|-----------|------|
| CPU | Intel i9-9900K · 8 cores / 16 threads · 3.60 GHz base |
| RAM | 128 GB DDR4 |
| Storage | 2× Samsung 1TB NVMe (MZVLB1T0HBLR) · RAID-1 mirror |
| Network | 1 Gbit |
| Location | Hetzner Helsinki (HEL1) |

---

## OS & Partition Layout

| | |
|---|---|
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| Kernel | 6.8.0-90-generic |
| Hostname | `cytools-hetzner` |
| RAID | mdadm RAID-1 across both NVMe (`/dev/md0`, `/dev/md1`) |

```
/boot            1 GB   ext4   /dev/md0
/               100 GB  ext4   LV vg0/root
/home           200 GB  ext4   LV vg0/home
/var/lib/docker 200 GB  ext4   LV vg0/docker
/tmp             50 GB  ext4   LV vg0/tmp
(unallocated)  ~400 GB         available in vg0 for future LVs
```

Extend storage if needed:
```bash
sudo lvcreate -L 100G -n data vg0
sudo mkfs.ext4 /dev/vg0/data
sudo mkdir /data && sudo mount /dev/vg0/data /data
echo '/dev/vg0/data /data ext4 defaults 0 2' | sudo tee -a /etc/fstab
```

---

## Software Stack

| Component | Version | Notes |
|-----------|---------|-------|
| Docker | 29.2.1 | CE, official repo |
| Python (container) | 3.12.11 | Debian Bookworm base |
| CYTools | 1.4.5 | with pplpy, python-flint, cysignals, gmpy2 |
| devcontainer CLI | 0.83.3 | Node.js 20.x |
| tmux | system | for long-running scans |
| git | system | repo at `~/cytools_project` |

User `seth` has: passwordless sudo, Docker group membership, SSH key auth.

---

## Dev Container

The CYTools environment runs inside a dev container built from `.devcontainer/Dockerfile`.

### Quick start (reconnecting)

```bash
ssh hetzner

# Check if container is running
docker ps

# If container is running, exec into it:
CONTAINER_ID=$(docker ps -q | head -1)
docker exec -it -w /workspaces/cytools_project $CONTAINER_ID bash

# If container is NOT running, rebuild and start:
cd ~/cytools_project
git pull
devcontainer up --workspace-folder .
```

### Run a scan inside the container

```bash
# One-off command (from host):
CONTAINER_ID=$(docker ps -q | head -1)
docker exec -w /workspaces/cytools_project $CONTAINER_ID \
  python -u scan_fast.py --h11 18 --workers 14

# Long-running scan in tmux (survives SSH disconnect):
tmux new-session -d -s myscan \
  "docker exec -w /workspaces/cytools_project $CONTAINER_ID \
   python -u scan_fast.py --h11 18 --workers 14 2>&1 \
   | tee ~/cytools_project/results/scan_log.txt"

# Check scan progress:
tmux capture-pane -t myscan -p | tail -20

# Attach to watch live:
tmux attach -t myscan
# (Ctrl-B, D to detach without stopping)

# List tmux sessions:
tmux ls
```

### Rebuild container (after Dockerfile changes)

```bash
cd ~/cytools_project
git pull
docker stop $(docker ps -q) 2>/dev/null
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .
```

### Key paths

| Location | What |
|----------|------|
| **Host**: `~/cytools_project/` | Git repo (bind-mounted into container) |
| **Host**: `~/cytools_project/results/` | Scan output CSVs (persisted on host) |
| **Container**: `/workspaces/cytools_project/` | Same repo, seen from inside container |

Results written inside the container at `/workspaces/cytools_project/results/` appear at `~/cytools_project/results/` on the host (bind mount), so they survive container restarts.

---

## VS Code Remote SSH

To use VS Code on your local machine connected to the Hetzner server:

1. Install the **Remote - SSH** extension in VS Code
2. Ensure `~/.ssh/config` has the `hetzner` host entry (see Connection section)
3. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host" → `hetzner`
4. Open folder: `/home/seth/cytools_project`
5. VS Code will detect `.devcontainer/` and prompt "Reopen in Container" — click yes
6. Terminal inside VS Code will be inside the container with CYTools ready

---

## Performance Benchmarks

| Scanner | Workers | h11 | Rate | vs Dell5 |
|---------|---------|-----|------|----------|
| `scan_fast.py` (T0.25) | 8 | 15 | **12.7 poly/s** | **5.3× faster** |
| `scan_fast.py` (T0.25) | 4 | 15 | ~7 poly/s (est) | ~3× faster |
| Dell5 `scan_fast.py` | 4 | 15 | 2.4 poly/s | baseline |

Recommended workers: **14** (leaves 2 threads for OS/Docker overhead).

---

## Estimated Scan Times (T0.25 at 12 poly/s)

| h¹¹ | Polytopes | Est. time (14 workers) |
|-----|-----------|----------------------|
| 18 | ~195,000 | ~4.5 hrs |
| 19 | ~440,000 | ~10 hrs |
| 20 | ~978,000 | ~23 hrs |
| 21 | ~1,900,000 | ~44 hrs |

---

## Maintenance

### Check RAID health
```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo mdadm --detail /dev/md1
```

### System updates
```bash
sudo apt update && sudo apt upgrade -y
```

### Hetzner Robot panel
- URL: https://robot.hetzner.com
- Manage server, request rescue mode, view bandwidth
- Support requests: via Robot UI (user icon → Support)

### If you need to reinstall
Boot into Hetzner Rescue System via Robot panel, then:
```bash
/root/.oldroot/nfs/install/installimage -a -c /tmp/install.conf
```
The install config used is documented in PROCESS_LOG.md (2026-02-24 entry).

### Blocked ports
Hetzner blocks outgoing ports 25 and 465 by default (anti-spam). Create a support request in Robot if you need them.
