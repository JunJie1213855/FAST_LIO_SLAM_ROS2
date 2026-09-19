import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # SC-A-LOAM for the MulRan dataset (ouster OS1-64)
    pkg_dir = get_package_share_directory('aloam_velodyne')

    rviz = LaunchConfiguration('rviz')

    # CHANGE THIS and end with /
    save_directory = os.path.join(
        os.path.expanduser('~'),
        'Documents', 'catkin2021', 'catkin_scaloam_util', 'data', '')

    scan_registration = Node(
        package='aloam_velodyne',
        executable='ascanRegistration',
        name='scanRegistration',
        output='screen',
        parameters=[{
            'scan_line': 64,
            'lidar_type': 'OS1-64',
            'minimum_range': 0.5,
        }],
        remappings=[
            ('/velodyne_points', '/os1_points'),
        ],
    )

    laser_odometry = Node(
        package='aloam_velodyne',
        executable='alaserOdometry',
        name='laserOdometry',
        output='screen',
        parameters=[{
            'mapping_skip_frame': 1,
        }],
    )

    laser_mapping = Node(
        package='aloam_velodyne',
        executable='alaserMapping',
        name='laserMapping',
        output='screen',
        parameters=[{
            'mapping_line_resolution': 0.4,
            'mapping_plane_resolution': 0.8,
        }],
    )

    laser_pgo = Node(
        package='aloam_velodyne',
        executable='alaserPGO',
        name='laserPGO',
        output='screen',
        parameters=[{
            'save_directory': save_directory,
            'keyframe_meter_gap': 1.0,
            'sc_dist_thres': 0.2,
            'sc_max_radius': 80.0,
        }],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', os.path.join(pkg_dir, 'rviz_cfg', 'aloam_velodyne.rviz')],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Launch RViz'),
        scan_registration,
        laser_odometry,
        laser_mapping,
        laser_pgo,
        rviz_node,
    ])
