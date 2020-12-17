from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def _requirements(file):
    return open(file).read().splitlines()


setup(
    name='launchable',
    license='Apache Software License v2',
    author='Launchable, Inc.',
    url='https://launchableinc.com/',
    author_email='info@launchableinc.com',
    description='Launchable CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=_requirements('requirements.txt'),
    packages=find_packages(),
    package_data={'launchable': ['jar/exe_deploy.jar']},
    setup_require=['setuptools_scm'],
    use_scm_version=True,
    entry_points={
        'console_scripts': [
            'launchable = launchable.__main__:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
