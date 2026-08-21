# Anna's Summer Robotics Project  -  Context File
*Paste this at the start of each new Claude session*

---

## Who I Am
- Anna, 17, Irish school student, based in Dublin
- Working with Shane (boyfriend) on a summer robotics portfolio project
- Shane is away 30 Jun - ~14 Jul, back for 2 days and then gone for 3 again
- School starts in ~7 weeks (mid-August)
- I have stress-related health issues  -  prefer focused work blocks, not marathons

---

## The Goal
Build a ROS2-based autonomous robot with:
- Mecanum wheel chassis (omnidirectional movement)
- LiDAR-based SLAM mapping and autonomous navigation
- Jetson Orin Nano Super as the compute platform
- Eventual goal: portfolio piece demonstrating robotics/AI skills

Inspiration: AI-powered autonomous car  -  starting from RC/keyboard control, progressing to voice control (Whisper on-device), then full SLAM autonomous navigation. Disney's BD-X droids (duck/penguin-like Star Wars bipedal bots) are a reference point for what on-device AI + robotics can achieve.

---

## Hardware

### Main Board & Kit Contents
Anna bought the **Yahboom Jetson Orin Nano Super 8GB "Off Superior Kit"** (Amazon UK, B0GTQ8BP61). All of the following are already in hand:

| Item | Notes |
|------|-------|
| Jetson Orin Nano 8GB module (P3767-0003) + carrier board (P3768-0000) | Core compute |
| 256GB NVMe SSD | Pre-installed; this is what we've been flashing |
| Power adapter | Powers the Jetson |
| WiFi antennas ×2 + M.2 Key E wireless card (pre-installed) | Built-in WiFi  -  no USB dongle needed |
| IMX219-77° CSI camera + camera case | **Used for Project #11 collision avoidance** |
| Acrylic case | Protective enclosure for Jetson |
| DP to HDMI cable | Connect Jetson to monitor |
| Type-C cable | USB-C connection |

- Originally came pre-flashed with JetPack 6.4.3 (working, had Ubuntu UI + could open apps)
- **Current status**: Running JetPack 7.2, fully set up
- Acrylic case assembled ✅
- IMX219 CSI camera mounted to case ✅
- Small touchscreen display connected (no longer needs external monitor) ✅
- Tiny Bluetooth keyboard set up ✅
- VS Code installed (ARM64 .deb) ✅
- Claude Code installed via npm (`sudo npm install -g @anthropic-ai/claude-code`) ✅

### Recovery Mode
- Short **pins 9 and 10** on Button Header J14 (the 2nd and 3rd pegs)
- Connect USB-C to PC
- Power on -> appears as APX device (VID:PID 0955:7523)

### Storage
- NVMe SSD (nvme0n1)  -  this is where JetPack installs
  - nvme0n1p1: APP partition, ext4, 233GB, UUID=695676c3-66fe-4cd1-ae4d-3046a730c5c2
  - nvme0n1p10: EFI partition, FAT32, 65MB
- Kingston 64GB USB  -  used as installer drive

### Robot Hardware
| Item | Status |
|------|--------|
| DWWTKL Mecanum Wheel Chassis (4WD, TT motors, metal) | ✅ Assembled |
| Vistreck L298N motor driver x2 | ✅ Arrived |
| ZOP 4S 14.8V 5500mAh LiPo battery (XT60) | ✅ Arrived ~11 Jul |
| LDROBOT D500 LiDAR sensor (ROS2 SDK) | ✅ Arrived  -  ordered LD19 but received D500, which is the upgraded replacement (same size, better performance, confirmed ROS2 Jazzy support) |
| Imax B6Ac LiPo battery charger | ✅ Arrived |
| Switian XT60 to DC5.5mm adapter cable | ✅ Arrived |
| Yizhet LM2596 buck converter x5 | ✅ Arrived |

### Important hardware notes
- TT motors are rated 3-6V. The 14.8V LiPo needs a **buck converter** (LM2596) stepped down to ~6V before going into L298N motor supply
- Jetson takes 9-20V DC, so 14.8V can power it directly
- L298N covers 2 motors each -> 2x L298N covers all 4 mecanum motors
- Chassis does NOT include motor wires  -  need to source separately
- Chassis mounting holes are Arduino-sized; may need to drill extra holes for Jetson

---

## Software Plan
- **OS**: JetPack 7.2 / L4T R39.2 / Ubuntu 24.04
- **ROS version**: ROS2 Jazzy
- **Key packages**: Nav2, SLAM Toolbox, RViz2, TF2
- **LiDAR driver**: LDROBOT D500 (received instead of LD19  -  direct upgrade). Use official ROS2 package: https://github.com/ldrobotSensorTeam/ldlidar_ros2. Confirmed working on ROS2 Jazzy.

---

## What's Been Done

### Jetson Boot History
1. Original JetPack 6.4.3 was **working** (had full Ubuntu UI, apps, even changed language settings)
2. Power was pulled mid-session -> corrupted boot chain
3. Kernel panic: `VFS: Unable to mount root fs on unknown-block(0,0)`  -  missing initrd
4. Tried manual EFI/GRUB fixes (didn't fully work)
5. Tried SDK Manager on Windows (Aorus PC + Shane's laptop)  -  both FAILED
   - Root cause: Jetson re-enumerates USB identity during flash reboot; Windows can't handle driver transition
   - WSL2 + usbipd also tried  -  failed due to stub driver binding issues
6. JetPack 7.2 ISO installer on Kingston USB (made with Rufus)
   - ISO: `jetsoninstaller-r39.2.0-2026-06-01-23-53-13-arm64.iso`
   - Written with Rufus 4.14, ISO mode, Grub 2.12 downloaded automatically
   - Accidentally selected "Boot from next volume" -> booted into Ubuntu successfully anyway
7. **Backup USB created**  -  second Kingston USB with JetPack 7.2, kept with kit box for emergencies

### Session  -  23 June 2026 ✅
- Verified Jetson booting correctly: `uname -r` -> `6.8.12-1021-tegra`, Ubuntu 24.04.4 LTS
- Installed WiFi antennas (both U.FL connectors on RTL8822CE card), connected to home WiFi
- Added ROS2 Jazzy apt repository and GPG key
- Installed `ros-jazzy-desktop` successfully
- Sourced ROS2 in `~/.bashrc`  -  confirmed working with `ros2 topic list`
- Installed `jetson-stats` 4.3.2

### Current Status
**SLAM mapping working (8 Aug).** Robot drives under ROS2 keyboard control, LiDAR publishes /scan, SLAM Toolbox builds and saves a map. Next milestone: mount LiDAR on chassis, get real wheel odometry, do a proper room map while driving.

---

## 7-Week Plan (revised 1 July)

| Week | Dates | Focus |
|------|-------|-------|
| 1 | ~23 Jun | ✅ Jetson boot, ROS2 installed, case + screen + keyboard, chassis assembled |
| 2 | 1-7 Jul | Udemy ROS2 course (~2hrs/day). LiDAR + cable arriving. |
| 3 | 7-13 Jul | Finish course. Connect LiDAR, visualise in RViz. Wire buck converters. |
| 4 | 14-20 Jul | Motor drivers + battery arrive. Wire motors + L298N. Get chassis moving via keyboard. |
| 5 | 21-27 Jul | Shane back ~21 Jul. Mount Jetson + LiDAR on chassis. SLAM with manual drive. |
| 6 | 28 Jul - 3 Aug | Autonomous navigation  -  goal-point driving |
| 7 | 4-10 Aug | Polish, demo video, portfolio writeup |

---

## Session  -  28 Jul - 4 Aug 2026 (Anna solo  -  hardware wiring + first drive)

### What got done
- Wired full power chain: LiPo -> XT60 -> split to (a) LM2596 buck converters -> L298N motor supply and (b) DC barrel jack -> Jetson
- Set both buck converters to ~6V output (adjusted with potentiometer, measured with multimeter)
- Wired both L298N motor supply terminals from buck converter OUT+ and OUT−
- Connected all 4 motor wire pairs to L298N outputs (OUT1-OUT4 on each board)
- Debugged and resolved GPIO issues (see GPIO section below)
- Discovered motor wiring polarity mismatch: FL and RL motors were physically wired in reverse relative to FR and RR
  - Fix: swapped IN_A/IN_B in code for FL and RL motor calls rather than rewiring hardware
- Resolved git merge conflict in mecanum_node.py (conflict from editing on Jetson AND laptop), pushed fix, pulled on Jetson, rebuilt
- Robot confirmed driving on all 4 wheels under ROS2 keyboard control (`teleop_twist_keyboard`)
- Verified: forward, backward, turning all working correctly
- Identified soldering issue: one GND wire on motor driver 2 had come loose  -  resoldered
- Electrical tape under one buck converter melted slightly during testing (source of earlier burning smell)  -  inspected, no damage to board
- Cable management still rough  -  tidy-up and sturdier mounting needed before next phase

### Electrical tape incident
During testing with the LiPo connected, a faint burning smell appeared. Source identified as electrical tape that had been placed underneath one of the buck converters  -  the tape made contact with a warm component. No damage to any board or wire. Tape was removed, all components tested and confirmed functional.

---

## GPIO Issue Deep-Dive

### Summary
Getting GPIO working on the Yahboom Jetson Orin Nano Super carrier board required solving two separate problems layered on top of each other.

### Problem 1  -  Jetson.GPIO doesn't recognise the Yahboom carrier board
Jetson.GPIO is NVIDIA's official Python library for GPIO. It works out-of-the-box on official Developer Kit carrier boards, but throws a warning on third-party boards like Yahboom's:

```
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNING: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
```

In practice, the library's BOARD pin -> gpiochip line mappings still worked for the Yahboom board because the Jetson module itself is standard (P3767-0003). The carrier board differences don't affect the pin numbering on the 40-pin header.

### Problem 2  -  PADCTL pinmux registers not configured (the real root cause)
Even when Jetson.GPIO (or gpiod/gpioset) claimed to be driving a pin HIGH, zero voltage appeared on the physical header pin. The GPIO controller was writing the signal correctly in software, but it wasn't reaching the physical pad.

The cause: on the Jetson Orin, each GPIO pad has a separate **PADCTL (pad control) register** in the SoC that controls the pad's function (GPIO, SPI, I2C, etc.). By default after boot, many pads are in a high-impedance or non-GPIO state. Until this register is configured, the GPIO controller's output signal is invisible on the physical pin.

The fix is to write `0x5` to the PADCTL register for each GPIO pin you want to use as an output. This enables the GPIO function on that pad. The setting persists in hardware until the next reboot (not across reboots), so it must be run once per boot.

The PADCTL registers were found by cross-referencing the Jetson Orin NX pin definitions in Jetson.GPIO's `gpio_pin_data.py`. The compatible string from `cat /proc/device-tree/compatible` matched `JETSON_ORIN_NANO` -> uses `JETSON_ORIN_NX_PIN_DEFS`.

### PADCTL addresses for all 8 motor GPIO pins

| BOARD pin | GPIO pad | PADCTL address |
|-----------|----------|----------------|
| 11 | PR.04 | 0x2430098 |
| 13 | PY.00 | 0x243D030 |
| 29 | PQ.05 | 0x2430068 |
| 31 | PQ.06 | 0x2430070 |
| 35 | PI.02 | 0x24340A0 |
| 37 | PY.02 | 0x243D048 |
| 38 | PI.01 | 0x2434098 |
| 40 | PI.00 | 0x2434090 |

### Problem 3  -  sudo vs non-sudo ROS2 DDS isolation
Running the mecanum_node as `sudo` (needed for `busybox devmem`) caused ROS2 DDS discovery to fail between the node and teleop_twist_keyboard (which runs as normal user). Root and non-root processes use separate DDS participant domains.

Fix: run the devmem commands as sudo first (they configure hardware registers, no process stays running), then launch the node as the normal user. The PADCTL config persists in hardware, so sudo is no longer needed for the node itself.

### "Device or resource busy" error
If a previous node run or `gpioset` process is still holding GPIO lines, the new run fails with `[Errno 16] Device or resource busy`. Fix: `sudo killall gpioset 2>/dev/null; pkill -f mecanum_node 2>/dev/null` before launching.

### Final working startup sequence (see startup_guide.md for full details)
1. Run 8 `sudo busybox devmem` commands (once per reboot) to configure PADCTL registers
2. Run `ros2 run mecanum_controller mecanum_node` as normal user
3. In a second terminal, run `ros2 run teleop_twist_keyboard teleop_twist_keyboard`

---

## Session  -  ~16-20 Jul 2026 (Anna solo  -  ROS2 workspace)

- Created `mecanum_robot_ws` ROS2 workspace with colcon build system
- Created `mecanum_controller` package with `mecanum_node.py`
  - Initially used PWM on pins 32, 36, 33, 15  -  got `ValueError: Channel 36 is not a PWM`
  - Root cause: Yahboom carrier board only exposes 2 hardware PWM pins (15 and 33), not 4
  - Fix: removed PWM entirely  -  motors run full speed only, direction controlled via IN pins, ENA/ENB jumpers stay ON on both L298Ns
  - Final node confirmed working on Jetson: "GPIO initialised" and "Mecanum controller ready"
- Created `robot_bringup` package with `robot.launch.py` (teleop node commented out for now)
- Pushed workspace to GitHub: https://github.com/annazeit/rosrover
- Cloned repo on Jetson and built with colcon
- Created supporting docs: `Robot_Architecture.md` (full node/topic/GPIO plan) and `Shane_Assembly_Session.md` (step-by-step wiring guide)
- GPIO pin assignments (BOARD numbering):
  - FL: pins 29, 31 | RL: pins 37, 38 | FR: pins 35, 40 | RR: pins 11, 13

---

## Session  -  ~21-25 Jul 2026 (with Shane  -  hardware wiring + LiDAR)

- Wired Jetson GPIO 40-pin header to both L298Ns (8 signal wires total, per assembly plan)
- Connected LDROBOT D500 LiDAR via USB to Jetson (`/dev/ttyUSB0`)
- Cloned `ldlidar_stl_ros2` into workspace: `https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2.git`
  - Build fix for Ubuntu 24.04 / newer GCC (pthread not implicitly included):
    `sed -i '1i#include <pthread.h>' ~/mecanum_robot_ws/src/ldlidar_stl_ros2/ldlidar_driver/src/logger/log_module.cpp`
  - Built successfully with colcon
- Added annaz to dialout group for USB serial access: `sudo usermod -aG dialout annaz`
  - Use `newgrp dialout` in current session without needing to reboot
- LiDAR confirmed working: publishing `/scan` at 230400 baud on `/dev/ttyUSB0`
- D500 uses LD19 launch files (direct upgraded replacement, same protocol):
  `ros2 launch ldlidar_stl_ros2 viewer_ld19.launch.py serial_port:=/dev/ttyUSB0`
- RViz scan visualisation confirmed  -  dots visible, LaserScan display on `/scan` topic
- Installed openssh-server on Jetson, enabled to auto-start on boot:
  ```
  sudo apt install openssh-server
  sudo systemctl enable ssh
  sudo systemctl start ssh
  ```
- Jetson IP: `192.168.0.210` (WiFi, interface wlP1p1s0)
- Passwordless SSH set up from laptop WSL: `ssh annaz@192.168.0.210`
  - Key generated in WSL with `ssh-keygen -t ed25519`, copied with `ssh-copy-id`
- RViz cannot open over SSH (no X display)  -  run node via SSH, open RViz on Jetson screen separately, or use `ld19.launch.py` (no RViz) via SSH

---

## Session  -  26 June 2026 (with Shane, ~4 hours)

**Plan:**
- **Shane**: Assemble mecanum chassis  -  frame, motors, solder motor wires if needed. Measure Jetson against chassis for mounting.
- **Anna**: Work through ROS2 beginner playlist (Articulated Robotics / "ROS2 Humble for Beginners"  -  concepts apply to Jazzy, skip install steps)
- **Together (last 30 min)**: assess Jetson mounting options on chassis, note any extra hardware needed (standoffs, screws)

---

## Key Technical Context

### Why SDK Manager failed
- Windows (any machine) cannot handle the Jetson's USB identity change during flash reboot
- WSL2 usbipd stub driver causes enumeration issues
- **Solution**: ISO installer bypasses SDK Manager entirely  -  NVIDIA's own recommended method as of JetPack 7.2

### grub.cfg (previous broken version on nvme0n1p10/EFI/BOOT/)
```
set default=0
set timeout=5
menuentry "Ubuntu" {
    search --no-floppy --fs-uuid --set=root 695676c3-66fe-4cd1-ae4d-3046a730c5c2
    linux /boot/Image root=UUID=695676c3-66fe-4cd1-ae4d-3046a730c5c2 rw rootwait console=ttyTCU0,115200 console=tty0
}
```
Issues: `search --fs-uuid` not available in minimal GRUB build; missing initrd line.

### Aorus PC (Windows 11, x86_64)
- Gigabyte gaming PC in Anna's house (belongs to someone else)
- Has WSL2 (Ubuntu 24.04) installed
- Has dented USB ports
- SDK Manager 2.4.1 installed in WSL2
- Used to create the bootable USB with Rufus

---

## People
- **Anna**: Main builder, 17, Dublin
- **Shane**: Collaborator/boyfriend, leaving ~30 Jun for 2 weeks, back ~14 Jul
- **Anna's dad**: Software engineer at Microsoft, aware of project

---

---

## Session  -  8 August 2026 (Anna solo  -  LiDAR SLAM + battery charger)

### Battery charger situation

The Imax B6Ac charger that arrived turned out to have only ~5 reviews on Amazon. Anna was already anxious about LiPo safety, and a nearly-unreviewed charger wasn't reassuring. Rather than risk a cheap clone, decided to **not touch the battery at all for now** and source a verified genuine charger separately.

Best option found: **SkyRC B6AC V2** from **yourFPV.co.uk** (Sheffield, UK). 671 Trustpilot reviews, 4.9/5 stars. Genuine units can be verified via scratch sticker at skyrc.com/antifake. Need to email sales@yourfpv.co.uk first to confirm they ship to Ireland before ordering.

For today's SLAM work, the Jetson ran on its own mains power adapter (no battery, no motors needed).

---

### SLAM Toolbox session  -  problems and fixes

The goal was to get SLAM Toolbox running with the LD19 LiDAR via X forwarding (ssh -X from laptop WSL -> RViz window appears on laptop), so mapping can later be done with the robot moving around.

#### What worked immediately
- LiDAR publishing `/scan` at 10Hz via `/dev/ttyUSB0` ✓
- `ssh -X` X forwarding from WSL2 -> RViz window on laptop ✓  
- `ros2 install slam_toolbox` and basic launch ✓
- LaserScan dots visible in RViz ✓

#### Problem 1  -  "Failed to compute odom pose" on every scan

slam_toolbox needs a TF chain: `map -> odom -> base_link -> base_laser`. The LiDAR launch already provides `base_link -> base_laser`. But nothing was providing `odom -> base_link` (that normally comes from wheel encoders, which aren't running).

slam_toolbox was logging "Failed to compute odom pose" on every single scan and never building a map.

**Attempted fixes that didn't fully work:**
- Passing `base_frame:=base_link` as a launch argument  -  the arg isn't wired through in slam_toolbox's launch file
- Publishing a static transform for `odom -> base_link` via `tf2_ros static_transform_publisher`  -  still failed (slam_toolbox's TF buffer wasn't receiving it reliably)
- `fake_odom.py` v1 publishing at 20Hz with current time  -  still failing

**Diagnostic:** wrote `tf_debug.py` to mimic slam_toolbox's internal TF lookup. It revealed **tf2 ExtrapolationException**  -  scan timestamps from the LD19 (~10Hz, 100ms apart) didn't always align with available TF buffer entries from fake_odom. Errors alternated between "into the past" and "into the future".

**Root cause:** slam_toolbox processes scans in its own C++ thread. By the time it looks up `odom -> base_link` at the scan's timestamp T, fake_odom may not have published a TF entry at time T yet  -  so tf2 says "into the future." With only 20Hz publishing, there were gaps.

**Fix:** Updated `fake_odom.py` to publish at 100Hz, and crucially, publish **two** TF entries per timer tick: one at `now` and one at `now + 300ms`. This ensures the scan timestamp always falls *between* two buffer entries (interpolation, not extrapolation), so tf2 can always resolve it.

```python
def timer_cb(self):
    now = self.get_clock().now()
    self.publish_tf(now.to_msg())
    future = now + rclpy.duration.Duration(nanoseconds=300_000_000)
    self.publish_tf(future.to_msg())
```

#### Problem 2  -  Wrong slam_toolbox launch argument name

After the TF fix, slam_toolbox went silent (no errors, but also no map). Checking params revealed the real problem:

```
ros2 param get /slam_toolbox base_frame  ->  base_footprint
ros2 param get /slam_toolbox transform_timeout  ->  0.2
```

Our params file was being **completely ignored**. The launch file accepts `slam_params_file`, not `params_file`  -  and since the wrong argument name was silently ignored, slam_toolbox used its defaults the entire time. Default `base_frame` is `base_footprint`, which doesn't exist in our TF tree, so every single lookup failed.

Additionally, the launch file defaults `use_sim_time` to `true`  -  wrong for real hardware (no `/clock` topic).

**Fix:**
```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=$HOME/slam_params.yaml \
  use_sim_time:=false
```

After this: `ros2 param get /slam_toolbox base_frame` -> `base_link` ✓. slam_toolbox logged "Registering sensor: [Custom Described Lidar]" and started processing scans.

#### Problem 3  -  Map not growing when walking around

The map appeared in RViz but stayed the same small area even when carrying the Jetson around the room. The LiDAR dots updated (showing the changing room layout) but the white map plane didn't grow.

**Root cause:** `minimum_travel_distance: 0.1`  -  slam_toolbox only adds new keyframes when it thinks the robot moved 10cm. But `fake_odom` always publishes identity (position 0,0,0), so slam_toolbox always thinks the robot hasn't moved and never adds new scans to the map.

**Fix:** Set both travel thresholds to zero in `slam_params.yaml`:
```yaml
minimum_travel_distance: 0.0
minimum_travel_heading: 0.0
```

After this, slam_toolbox accepted every scan and the map grew properly.

#### Problem 4  -  map_saver timing out

`ros2 run nav2_map_server map_saver_cli -f ~/my_map` was failing with "Failed to spin map subscription." slam_toolbox publishes `/map` only every 10 seconds, but map_saver's default timeout is 2 seconds.

**Fix:** `--ros-args -p save_map_timeout:=15.0`

#### Final result

Map saved successfully: **121×167 cells @ 5cm/pixel** ≈ 6×8 metres. Walls and open space clearly visible. Some drift/ghosting is expected without real odometry  -  scan-matching alone accumulates error over time.

---

### Key files created on Jetson today

| File | Purpose |
|------|---------|
| `~/fake_odom.py` | Publishes `odom -> base_link` TF at 100Hz + 300ms future timestamps. Required for SLAM without wheel encoders. |
| `~/slam_params.yaml` | slam_toolbox config: base_frame=base_link, minimum_travel=0, transform_timeout=1.0 |
| `~/my_map.pgm` + `~/my_map.yaml` | First saved map of the room |

See `startup_guide.md` for the full SLAM startup command sequence.

---

### What's still to do

- Order SkyRC B6AC V2 from yourFPV.co.uk (email first to confirm Ireland shipping)
- Fix front left wheel going backward only (ribbon cable or motor terminal issue, pins 11/13)
- Mount LiDAR securely on chassis
- Get real wheel odometry (encoders or dead-reckoning from motor commands) for accurate maps
- Make GPIO devmem commands run at boot automatically (systemd service)
- Full room mapping while driving the robot
- Autonomous navigation (Nav2 goal-point driving)

---

## Notes for Claude
- Anna is 17 and relatively new to hardware  -  explain things clearly but don't be condescending
- She's using her laptop to talk to Claude
- Jetson now has its own small touchscreen display and Bluetooth keyboard  -  fully standalone
- Prefer short, direct answers over long explanations unless she asks
- She responds well to honest assessments, including when things aren't going well
