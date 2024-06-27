from setuptools import setup
import os
from glob import glob

package_name = 'charmie_debug'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='utilizador',
    maintainer_email='tiagoribeiro80@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "calibrate_door_handle = charmie_debug.calibrate_door_handle:main",
            "debug_arm = charmie_debug.debug_arm:main",
            "debug_audio = charmie_debug.debug_audio:main",
            "debug_detect_distance_door = charmie_debug.debug_detect_distance_door:main",
            "debug_inspection_person_detection = charmie_debug.debug_inspection_person_detection:main",
            "debug_main = charmie_debug.debug_main:main",
            "debug_navigation_localization = charmie_debug.debug_navigation_localization:main",
            "debug_obstacles = charmie_debug.debug_obstacles:main",
            "debug_pick_object_depth = charmie_debug.debug_pick_object_depth:main",
            "debug_pick_place_all_objects = charmie_debug.debug_pick_place_all_objects:main",
            "debug_search_for_person = charmie_debug.debug_search_for_person:main",
		    "debug_spkr_face = charmie_debug.debug_spkr_face:main",
		    "debug_visual = charmie_debug.debug_visual:main",
            "debug_yolos = charmie_debug.debug_yolos:main",
		    "node_template = charmie_debug.node_template:main",
            "rosbag_2_video_converter = charmie_debug.rosbag_2_video_converter:main",
		    "task_template = charmie_debug.task_template:main"
        ],
    },
)
