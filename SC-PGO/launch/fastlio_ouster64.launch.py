import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Scan Context PGO consuming the output of FAST-LIO2 (ouster OS1-64).
    # The ROS2 port of laserPGO subscribes to /velodyne_cloud_registered_local and
    # /aft_mapped_to_init, which are remapped to FAST-LIO's /cloud_registered_body and
    # /Odometry. (ROS1's /cloud_for_scancontext remap has no equivalent in the port.)
    pkg_dir = get_package_share_directory('aloam_velodyne')

    rvizscpgo = LaunchConfiguration('rvizscpgo')

    # CHANGE THIS and end with /
    save_directory = os.path.join(
        os.path.expanduser('~'),
        'Desktop', 'catkin_fastlio_slam', 'data', '')

    laser_pgo = Node(
        package='aloam_velodyne',
        executable='alaserPGO',
        name='laserPGO',
        output='screen',
        parameters=[{
            'scan_line': 64,
            'lidar_type': 'OS1-64',
            'minimum_range': 0.5,
            'mapping_line_resolution': 0.4,
            'mapping_plane_resolution': 0.8,
            'mapviz_filter_size': 0.05,
            'keyframe_meter_gap': 0.5,
            'sc_dist_thres': 0.3,
            'sc_max_radius': 80.0,
            'save_directory': save_directory,
        }],
        remappings=[
            ('/aft_mapped_to_init', '/Odometry'),
            ('/velodyne_cloud_registered_local', '/cloud_registered_body'),
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rvizscpgo',
        arguments=['-d', os.path.join(pkg_dir, 'rviz_cfg', 'aloam_velodyne.rviz')],
        condition=IfCondition(rvizscpgo),
    )

    return LaunchDescription([
        DeclareLaunchArgument('rvizscpgo', default_value='true', description='Launch RViz'),
        laser_pgo,
        rviz_node,
    ])
