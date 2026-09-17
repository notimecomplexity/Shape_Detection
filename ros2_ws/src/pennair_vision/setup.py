from glob import glob
from setuptools import setup

setup(
    name='pennair_vision', version='0.1.0', packages=['pennair_vision'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/pennair_vision']),
        ('share/pennair_vision', ['package.xml']),
        ('share/pennair_vision/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Darren', maintainer_email='chdyuen@engineering.upenn.edu',
    description='An Agnostic Algorithm that detects 2D shapes on a background in a video, sketches their outlines, and maps their 3D coordinates.',
    license='LicenseRef-Proprietary',
    entry_points={'console_scripts': [
        'video_publisher = pennair_vision.video_publisher:main',
        'shape_detector = pennair_vision.shape_detector:main',
    ]},
)
