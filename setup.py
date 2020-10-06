from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'launchable',
    version = '0.0.1',
    license = 'MIT',
    author = 'Satoshi Asano',
    url = 'https://launchableinc.com/',
    author_email = 'sasano@launchableinc.com',
    description = 'Launchable CLI',
    install_requires = ['setuptools'],
    packages = ["launchable"],
    entry_points = {
        'console_scripts': [
            'launchable = launchable.cli:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)