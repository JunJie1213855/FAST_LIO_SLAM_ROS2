from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():
    # Debug example: run fastlio_mapping under gdb.
    # ROS1 param names were adapted to the ROS2 port's names:
    #   imu_topic  -> common/imu_topic
    #   fov_degree -> mapping/fov_degree
    # (ROS1's dense_map_enable has no equivalent in the ROS2 port and is dropped.)
    debug_params = {
        'common/imu_topic': '/livox/imu',
        'map_file_path': ' ',
        'max_iteration': 4,
        'mapping/fov_degree': 75.0,
        'filter_size_corner': 0.2,
        'filter_size_surf': 0.2,
        'filter_size_map': 0.5,
        'runtime_pos_log_enable': True,
        'cube_side_length': 2000.0,
    }

    laser_mapping = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        name='laserMapping',
        output='screen',
        prefix='gdb -ex run --args',
        parameters=[debug_params],
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Launch RViz'),
        laser_mapping,
    ])
