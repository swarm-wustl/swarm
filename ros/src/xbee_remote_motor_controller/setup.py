from setuptools import find_packages, setup

package_name = 'xbee_remote_motor_controller'

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
    maintainer='julian',
    maintainer_email='julian.clark4455@gmail.com',
    description='A simple package to send instructions from a computer to a robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'remote_controller = xbee_remote_motor_controller.remote_controller:main',
            'rc_motor_driver = xbee_remote_motor_controller.rc_motor_driver:main'
        ],
    },
)
