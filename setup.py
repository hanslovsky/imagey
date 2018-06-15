from distutils.core import setup
from distutils.command.build_py import build_py

setup(
    name='imagey',
    version='0.1.1-dev',
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='imagey launcher',
    url='https://github.com/hanslovsky/imagey',
    packages=['imagey'],
    entry_points={
        'console_scripts': [
            'imagey=imagey.imagey:main'
        ]
    },
)
