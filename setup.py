from setuptools import setup

setup(
   name='binary-music-analyzer',
   version='0.1',
   description='Scans your music for a hidden message.',
   author='Jan Peter Skambraks and Bjarne Magnussen',
   author_email='bjarne.magnussen@gmail.com',
   maintainer='Bjarne Magnussen',
   maintainer_email='bjarne.magnussen@gmail.com',
   url='https://github.com/Janska/binary-music-analyzer',
   download_url='https://github.com/Janska/binary-music-analyzer',
   license='MIT',

   keywords=(
       'music',
       'binary',
       'steganography',
   ),

   packages=['binary-music-analyzer'],
   install_requires=['aubio', 'numpy', 'scipy']
)
