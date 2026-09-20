import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # SC-PGO backend (laserPGO: ScanContext loop closure + GTSAM pose graph)
    # fed by Point-LIO instead of the A-LOAM / FAST-LIO frontend.
    #
    # Interface:
    #   Point-LIO publishes  /aft_mapped_to_init         (nav_msgs/Odometry)  -> matches laserPGO's topic directly
    #   Point-LIO publishes  /cloud_registered_body      (PointCloud2, "body" frame) -> remapped to laserPGO's /velodyne_cloud_registered_local
    #   (requires `publish.scan_bodyframe_pub_en: true` in the Point-LIO config)
    pkg_dir = get_package_share_directory('aloam_velodyne')

    rviz = LaunchConfiguration('rviz')
    save_directory = LaunchConfiguration('save_directory')

    laser_pgo = Node(
        package='aloam_velodyne',
        executable='alaserPGO',
        name='laserPGO',
        output='screen',
        parameters=[{
            'save_directory': save_directory,     # must be writable and end with '/'
            'keyframe_meter_gap': 1.0,
            'keyframe_deg_gap': 10.0,
            'sc_dist_thres': 0.2,
            'sc_max_radius': 80.0,                # 80 for outdoor, 20-40 for indoor
            'mapviz_filter_size': 0.4,
        }],
        remappings=[
            ('/velodyne_cloud_registered_local', '/cloud_registered_body'),
            # /aft_mapped_to_init needs no remap: Point-LIO already publishes it.
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_scpgo',
        arguments=['-d', os.path.join(pkg_dir, 'rviz_cfg', 'aloam_velodyne.rviz')],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='Launch a second RViz for SC-PGO (Point-LIO already starts its own)'),
        DeclareLaunchArgument(
            'save_directory',
            default_value=os.path.join(os.path.expanduser('~'), 'sc_pgo_data', ''),
            description='Output directory for SC-PGO scans/odometry (must end with /)'),
        laser_pgo,
        rviz_node,
    ])
