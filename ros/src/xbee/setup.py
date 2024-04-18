from setuptools import find_packages, setup

package_name = 'xbee'

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
    maintainer='sebtheiler',
    maintainer_email='25444757+sebtheiler@users.noreply.github.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'xbee_srv = xbee.xbee_srv:main',
            'xbee_test_send = xbee.xbee_test_send:main',
        ],
    },
)
