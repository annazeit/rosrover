# How to Reflash the Jetson Orin Nano Super
*Anna's personal guide - Yahboom Jetson Orin Nano Super 8GB*

---

## What you need

- Kingston 64GB USB (dedicated to JetPack 7.2 - keep it plugged into the Jetson kit box)
- Aorus PC (Windows 11) - for Rufus if you ever need to redo the USB
- HDMI cable + monitor
- Power adapter for the Jetson
- USB-C cable (from the kit)

---

## When do you need to reflash?

- Jetson won't boot (black screen with flashing cursor, no Ubuntu UI)
- Kernel panic on boot
- You've broken something in the OS and can't recover it
- You want a completely clean slate

---

## Step 1 - Recreate the USB (only if needed)

If the Kingston USB already has JetPack 7.2 on it, skip to Step 2.

If you need to redo it:

1. Download the ISO on the Aorus PC - paste this URL directly into Chrome and press Enter:
   ```
   https://developer.nvidia.com/downloads/embedded/L4T/r39_Release_v2.0/iso/jetsoninstaller-r39.2.0-2026-06-01-23-53-13-arm64.iso
   ```
   It's ~5-6 GB and will take a while.

2. Open **Rufus** (rufus-4.14.exe - keep a copy in your Downloads)

3. Settings in Rufus:
   - **Device**: Kingston USB (64 GB)
   - **Boot selection**: click SELECT -> find the ISO you just downloaded
   - When asked about ISO Hybrid: choose **"Write in ISO Image mode (Recommended)"**
   - When asked about Grub version: click **Yes** (lets it download matching Grub)
   - Confirm the warning about wiping the USB: click **OK**

4. Wait for the status bar to say **READY** before unplugging.

---

## Step 2 - Put the Jetson into recovery mode

Recovery mode is how the Jetson boots from USB instead of NVMe.

1. Make sure the Jetson is **powered off and unplugged**
2. Plug the **Kingston USB** into one of the Jetson's USB ports
3. Find the **Button Header J14** - the row of pins near the edge of the carrier board
4. **Short pins 9 and 10** (the 2nd and 3rd pegs from the left) - use a jumper cap, a piece of wire, or a metal tweezer tip, held in place
5. While holding pins 9-10 shorted, plug in the **power adapter** and power on
6. You can release the short after about 2 seconds

---

## Step 3 - Boot the installer

1. Connect the Jetson to the monitor via HDMI
2. Power on - after a few seconds you'll see a simple text menu:

   ```
   * Install Jetson ISO r39.2.0
     Boot from next volume
     UEFI Firmware Settings
   ```

3. **Select "Install Jetson ISO r39.2.0"** (it should already be highlighted - just press Enter)

   **Do NOT** accidentally select "Boot from next volume" - that skips the installer

---

## Step 4 - Run the installer

The installer runs automatically. It will:
- Wipe the NVMe SSD completely
- Install a fresh JetPack 7.2 (Ubuntu 24.04) onto it
- Take roughly 15-30 minutes

The screen will show progress. Don't touch anything. When it's done it will either reboot automatically or show a completion message.

---

## Step 5 - Verify it worked

1. Remove the Kingston USB after the installer finishes
2. Power cycle the Jetson (unplug and replug power)
3. It should boot directly into Ubuntu - you'll see the NVIDIA logo, then the Ubuntu desktop
4. Open a terminal and run:
   ```bash
   uname -r
   ```
   You should see a kernel version like `6.8.x-...`

5. Also run:
   ```bash
   cat /etc/os-release
   ```
   Should say Ubuntu 24.04.

---

## Step 6 - After a reflash, reinstall your tools

Every reflash is a clean slate, so you'll need to reinstall:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install ROS 2 Jazzy
sudo apt install ros-jazzy-desktop -y

# Install jetson-stats
sudo pip3 install jetson-stats

# Source ROS 2 automatically on every terminal open
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Keep your project code backed up on GitHub so you never lose it during a reflash.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Menu doesn't appear, just black screen | USB may not be seated properly - try a different USB port on the Jetson |
| "Boot from next volume" selected by accident | Power cycle and try again - no harm done |
| Installer crashes halfway | Power cycle, boot USB again, select installer again |
| Ubuntu boots but feels broken after install | Run `sudo apt update && sudo apt upgrade -y` first before anything else |
| Jetson not detected in recovery mode | Make sure pins 9-10 are shorted BEFORE powering on, not after |

---

*Last updated: June 2026  -  JetPack 7.2 / L4T R39.2 / Ubuntu 24.04*
