from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='plex-remote',
    version='1.0.2',
    author="Gerben Droogers",
    author_email="plexremote@g4d.nl",
    description="A library for easy implementing a remote plex client",
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tijder/plex-remote",
    packages=['plex_remote'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests']
)
