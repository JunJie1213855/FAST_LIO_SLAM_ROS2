# FAST_LIO_SLAM (ROS2)

A LiDAR-inertial SLAM system with loop closure, ported to **ROS2 Humble**.

- **Odometry**: [Point-LIO](https://github.com/hku-mars/Point-LIO) (a robust LiDAR-inertial odometry, replaces the original FAST-LIO2 frontend)
- **Loop closure & pose-graph optimization**: [SC-PGO](https://github.com/gisbi-kim/SC-A-LOAM) — [Scan Context](https://github.com/irapkaist/scancontext)-based loop detection + [GTSAM](https://github.com/borglab/gtsam)-based pose-graph optimization

> The original ROS1 `FAST_LIO_SLAM` frontend (FAST-LIO2) has been replaced by **Point-LIO** in this port.

---

## Architecture

```
                    ┌────────────────────────────────────┐
  LiDAR + IMU  ───▶ │  Point-LIO (pointlio_mapping)      │   LIO frontend
                    │  /unilidar/cloud, /unilidar/imu    │
                    └───────────────┬────────────────────┘
                                    │  /aft_mapped_to_init        (Odometry)
                                    │  /cloud_registered_body     (body-frame cloud)
                                    ▼
                    ┌────────────────────────────────────┐
                    │  laserPGO (alaserPGO)               │   SC-PGO backend
                    │  ScanContext loop + GTSAM pose graph│
                    └───────────────┬────────────────────┘
                                    │  /aft_pgo_path, /aft_pgo_map,
                                    │  /aft_pgo_odom, /loop_scan_local, /loop_submap_local
                                    ▼
                              optimized map / trajectory
```

The frontend (Point-LIO) and the backend (laserPGO) run as **separate nodes** — Point-LIO produces odometry + a local (ego-centric) point cloud, and laserPGO consumes them for loop closure and pose-graph optimization.

---

## Packages

| Directory | ROS2 package | Role |
|---|---|---|
| `Point_LIO/` | `point_lio` | LiDAR-inertial odometry frontend |
| `SC-PGO/` | `aloam_velodyne` | ScanContext loop closure + GTSAM pose-graph backend |

### Executables

- `point_lio` → `pointlio_mapping` (node `laserMapping`)
- `aloam_velodyne` → `alaserPGO` (SC-PGO backend)

---

## Dependencies

ROS2 Humble + standard perception stack:

- `pcl`, `pcl_ros`, `pcl_conversions`
- `Eigen3`, `Sophus` (Point-LIO)
- `Ceres`, `OpenCV` (SC-PGO)
- **`GTSAM`** (required for SC-PGO — install with `sudo apt install ros-humble-... ` or from source)
- `livox_ros_driver2` (only for Livox lidars; otherwise Point-LIO's `lidar_type` ignores it)

```bash
sudo apt install ros-humble-pcl-ros ros-humble-pcl-conversions ros-humble-cv-bridge
# GTSAM: e.g. via apt (if available) or build from https://github.com/borglab/gtsam
```

---

## Build

```bash
cd ~/rosws/Fast_lio_slam_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

Build only the SLAM packages:

```bash
colcon build --packages-select point_lio aloam_velodyne
```

---

## How to use (Point-LIO + SC-PGO)

### Terminal 1 — Point-LIO frontend

```bash
source ~/rosws/Fast_lio_slam_ws/install/setup.bash
ros2 launch point_lio point_lio_unitree.launch.py       # default: config/unilidar_l1.yaml
```

Or specify another lidar config (see below):

```bash
ros2 launch point_lio point_lio.launch.py point_lio_cfg_dir:=/path/to/your.yaml
```

### Terminal 2 — SC-PGO backend (laserPGO)

```bash
source ~/rosws/Fast_lio_slam_ws/install/setup.bash
ros2 launch aloam_velodyne pointlio_scpgo.launch.py \
    save_directory:=$HOME/sc_pgo_data/ \
    rviz:=true
```

- `save_directory` must be writable and end with `/` (laserPGO saves scans/odometry here).
- `rviz:=true` opens the SC-PGO RViz config (shows `/aft_pgo_path`, `/aft_pgo_map`, `/aft_pgo_odom`, loop-closure scans).

---

## Topic interface (Point-LIO → laserPGO)

Point-LIO publishes, and `laserPGO` subscribes to:

| Point-LIO topic | Type | laserPGO subscription | Note |
|---|---|---|---|
| `/aft_mapped_to_init` | `nav_msgs/Odometry` | `/aft_mapped_to_init` | same name, no remap |
| `/cloud_registered_body` | `sensor_msgs/PointCloud2` | `/velodyne_cloud_registered_local` | remapped in `pointlio_scpgo.launch.py` |
| (optional) — | `sensor_msgs/NavSatFix` | `/gps/fix` | not required; runs without GPS priors |

> **Important**: `/cloud_registered_body` is only published when the Point-LIO config sets
> `publish.scan_bodyframe_pub_en: true`. The body-frame cloud is what ScanContext needs
> (ego-centric, not world-frame).

`laserPGO` publishes (for visualization):

- `/aft_pgo_path` — optimized trajectory (green in RViz)
- `/aft_pgo_map` — optimized global map
- `/aft_pgo_odom` — current optimized pose
- `/loop_scan_local`, `/loop_submap_local` — loop-closure match pairs (appear when a loop is detected)

---

## Point-LIO config files (`Point_LIO/config/`)

| Config | Lidar | `lidar_type` | `scan_line` | `lid_topic` |
|---|---|---|---|---|
| `unilidar_l1.yaml` | UniLidar L1 | 6 | 18 | `/unilidar/cloud` |
| `kaist.yaml` | MulRan (Ouster OS1-64) | 3 | 64 | `/os1_points` |
| `ouster64.yaml` | Ouster OS1-64 | 3 | 64 | `os_cloud_node/points` |
| `velody16.yaml` | Velodyne VLP-16 | 2 | 32 ⚠️ | `velodyne_points` |
| `avia.yaml` | Livox AVIA | 1 | 6 | `livox/lidar` |
| `horizon.yaml` | Livox Horizon | 1 | 6 | `livox/lidar` |
| `mid360.yaml` | Livox Mid-360 | 2 | 4 | `livox/lidar` |
| `mid360_real.yaml` | Livox Mid-360 | 1 | 4 | `livox/lidar` |
| `mid360_sim.yaml` | Mid-360 (VLP-16-style sim) | 2 | 50 | `velodyne_points` |
| `robosenseAiry.yaml` | RoboSense Airy | 5 | 96 | `/rslidar_points` |

> ⚠️ `velody16.yaml` still has `scan_line: 32`; for a real VLP-16 change it to `16`.

Key parameters to check for your sensor: `common.lid_topic` / `common.imu_topic`,
`preprocess.lidar_type` / `scan_line` / `timestamp_unit`, `mapping.gravity` / `gravity_init`
(IMU mounting tilt), `mapping.extrinsic_T` / `extrinsic_R` (LiDAR↔IMU transform).

---

## Known fixes / notes

- **Negative timestamps in SC-PGO**: the ROS2 port used `rclcpp::Time(seconds * 10e9)` to convert
  seconds→nanoseconds; `10e9` is `1e10`, which overflowed `int64_t` and produced negative
  timestamps (crashing RViz with `cannot store a negative time point`). Fixed to `* 1e9` across
  `laserPosegraphOptimization.cpp`.
- `alaserPGO` clears `<save_directory>/Scans/` on startup (`rm -r` then `mkdir -p`); the
  "cannot remove" message on first run is harmless.

---

## Acknowledgements

- [Point-LIO](https://github.com/hku-mars/Point-LIO) authors (HKU MARS Lab)
- [FAST-LIO2](https://github.com/hku-mars/FAST_LIO) authors
- [SC-A-LOAM / SC-PGO](https://github.com/gisbi-kim/SC-A-LOAM) and [Scan Context](https://github.com/irapkaist/scancontext)
- Original [FAST_LIO_SLAM](https://github.com/gisbi-kim/FAST_LIO_SLAM)
