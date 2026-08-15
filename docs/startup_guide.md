# Robot Startup Guide

Everything you need to get the robot moving from a cold boot.

---

## Power Chain

```
LiPo 14.8V (XT60)
    │
    ├── DC barrel jack → Jetson (powers compute)
    │
    └── Split to both LM2596 buck converters (set to ~6V)
            │
            ├── Buck #1 OUT+ → L298N #1 VS (motor supply)
            │   Buck #1 OUT− → L298N #1 GND
            │
            └── Buck #2 OUT+ → L298N #2 VS (motor supply)
                Buck #2 OUT− → L298N #2 GND
```

---

## GPIO Pin Layout (Jetson 40-pin header → L298N)

**L298N #1**  -  controls RL (rear left) and FL (front left) motors

| Jetson BOARD pin | Wire goes to | Controls |
|-----------------|--------------|---------|
| 29 | IN1 | RL direction A |
| 31 | IN2 | RL direction B |
| 37 | IN3 | FL direction A |
| 38 | IN4 | FL direction B |
| GND (any) | GND | shared ground |

**L298N #2**  -  controls FR (front right) and RR (rear right) motors

| Jetson BOARD pin | Wire goes to | Controls |
|-----------------|--------------|---------|
| 35 | IN1 | FR direction A |
| 40 | IN2 | FR direction B |
| 11 | IN3 | RR direction A |
| 13 | IN4 | RR direction B |
| GND (any) | GND | shared ground |

**ENA and ENB jumpers must be ON** on both L298N boards (full speed, no PWM).

**Motor outputs:**
- L298N #1: OUT1/OUT2 → RL motor, OUT3/OUT4 → FL motor
- L298N #2: OUT1/OUT2 → FR motor, OUT3/OUT4 → RR motor

---

## Startup Commands (run on Jetson after every reboot)

### Step 1  -  Configure GPIO pinmux (run once per boot)

Open a terminal on the Jetson and run all 8 lines:

```bash
sudo busybox devmem 0x2430068 w 0x5  # pin 29 (RL_IN1)
sudo busybox devmem 0x2430070 w 0x5  # pin 31 (RL_IN2)
sudo busybox devmem 0x243D048 w 0x5  # pin 37 (FL_IN1)
sudo busybox devmem 0x2434098 w 0x5  # pin 38 (FL_IN2)
sudo busybox devmem 0x24340A0 w 0x5  # pin 35 (FR_IN1)
sudo busybox devmem 0x2434090 w 0x5  # pin 40 (FR_IN2)
sudo busybox devmem 0x2430098 w 0x5  # pin 11 (RR_IN1)
sudo busybox devmem 0x243D030 w 0x5  # pin 13 (RR_IN2)
```

### Step 2  -  Terminal 1: start the motor controller

```bash
ros2 run mecanum_controller mecanum_node
```

Expected output: `Mecanum controller ready`

### Step 3  -  Terminal 2: start keyboard control

Two options  -  pick one:

**Option A: Arrow teleop (recommended)**
Uses arrow keys. Hold a key to drive, release to stop.

```bash
ros2 run mecanum_controller arrow_teleop
```

| Key | Movement |
|-----|----------|
| `↑` | Forward |
| `↓` | Backward |
| `←` | Rotate left |
| `→` | Rotate right |
| `q` | Quit |

**Option B: teleop_twist_keyboard (original)**
Uses letter keys. Press once to set speed, `k` to stop.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

| Key | Movement |
|-----|----------|
| `i` | Forward |
| `,` | Backward |
| `j` | Rotate left |
| `l` | Rotate right |
| `u` | Forward + rotate left |
| `o` | Forward + rotate right |
| `k` | Stop |

Speed up/down: `q`/`z`  -  increase/decrease linear and angular speed together.

---

## If the node crashes with "Device or resource busy"

A previous run is still holding the GPIO lines. Kill it first:

```bash
sudo killall gpioset 2>/dev/null; pkill -f mecanum_node 2>/dev/null
```

Then repeat Steps 1–3.

---

## Connecting via SSH

### Step 1 - Connect the Jetson to your WiFi

With a monitor and keyboard plugged into the Jetson and the Jetson powered on, connect to your WiFi network via Settings.

Then open a terminal and find the Jetson's IP address:

```bash
hostname -I
```

The number it prints (e.g. `192.168.1.45`) is the Jetson's IP. Write it down.

### Step 2 - SSH in from your laptop

Open WSL on your laptop and run:

```bash
ssh annaz@192.168.x.x
```

Replace `192.168.x.x` with the IP you found above. When asked for a password, enter the Jetson's password (ask Anna).

Open more WSL windows and SSH in again for each extra terminal you need (the startup needs 2 terminals minimum).

### Step 3 - Get the robot moving

Once SSH'd in, follow the normal startup sequence from the top of this guide:

1. Run all 8 `sudo busybox devmem` commands in your first terminal
2. In that same terminal: `ros2 run mecanum_controller mecanum_node`
3. In a second SSH terminal: `ros2 run mecanum_controller arrow_teleop`

Use arrow keys to drive. Note: the front left wheel currently only spins backwards - this is a known hardware issue being investigated.

---

## LiDAR + SLAM mapping (run from laptop via SSH)

Plug in LD19 via USB. Open 4 SSH terminals into the Jetson (`ssh annaz@192.168.0.210`).
For RViz use `ssh -X annaz@192.168.0.210` so the window appears on your laptop.

### Terminal 1  -  LiDAR

```bash
ros2 launch ldlidar_stl_ros2 ld19.launch.py serial_port:=/dev/ttyUSB0
```

### Terminal 2  -  Fake odometry (no wheel encoders needed)

```bash
python3 ~/fake_odom.py
```

### Terminal 3  -  SLAM Toolbox

```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=$HOME/slam_params.yaml \
  use_sim_time:=false
```

Expected: `Registering sensor: [Custom Described Lidar]`  -  means it's working.
No output after that is normal (errors would appear if something was wrong).

### Terminal 4  -  RViz (via ssh -X session)

```bash
rviz2
```

In RViz: set Fixed Frame to `map`, add a **Map** display on `/map`, add a **LaserScan** display on `/scan`.

### Saving the map

Walk around the room carrying the robot, then run:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map --ros-args -p save_map_timeout:=15.0
```

Saves `~/my_map.pgm` and `~/my_map.yaml` on the Jetson.

---

### Key files on Jetson

| File | Purpose |
|------|---------|
| `~/fake_odom.py` | Publishes odom→base_link TF at 100Hz (required for SLAM without wheel encoders) |
| `~/slam_params.yaml` | SLAM Toolbox config (base_frame: base_link, use_scan_matching: true) |
| `~/my_map.pgm` / `~/my_map.yaml` | Saved map |

---

### Troubleshooting SLAM

**"Failed to compute odom pose" spam**  -  fake_odom isn't running, or slam_toolbox was launched with wrong args. Make sure to use `slam_params_file:=` (not `params_file:=`) and `use_sim_time:=false`.

**Map not appearing in RViz**  -  check `/map` is publishing: `ros2 topic hz /map`. If publisher count on `/scan` is 0, the LiDAR node died  -  restart Terminal 1.

**map_saver "Failed to spin map subscription"**  -  add `--ros-args -p save_map_timeout:=15.0` to give it time to receive the map (publishes every 10s).
