from setuptools import find_packages, setup

package_name = 'turtle_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rony',
    maintainer_email='rony.kaddoum.2013@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'wall_finder_server = turtle_controller.wall_finder_srv:main',
        	'driver_node = turtle_controller.robot_driver:main',
            'tester_node = turtle_controller.tester_node:main'
        ],
    },
)
