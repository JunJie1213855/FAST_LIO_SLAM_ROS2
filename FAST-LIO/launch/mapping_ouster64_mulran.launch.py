import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch file for ouster OS2-64 LiDAR (MulRan dataset)
    pkg_dir = get_package_share_directory('fast_lio')

    rviz = LaunchConfiguration('rviz')

    extra_params = {
        'feature_extract_enable': False,
        'point_filter_num': 3,
        'max_iteration': 3,
        'filter_size_surf': 0.5,
        'filter_size_map': 0.5,
        'cube_side_length': 1000.0,
        'runtime_pos_log_enable': False,
        'pcd_save_enable': False,
    }

    laser_mapping = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        name='laserMapping',
        output='screen',
        parameters=[
            os.path.join(pkg_dir, 'config', 'ouster64_mulran.yaml'),
            extra_params,
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', os.path.join(pkg_dir, 'rviz_cfg', 'loam_livox.rviz')],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Launch RViz'),
        laser_mapping,
        rviz_node,
    ])
